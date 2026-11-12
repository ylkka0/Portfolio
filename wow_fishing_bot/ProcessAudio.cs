// Windows application loopback. PCM16, stereo, 48 kHz to stdout; diagnostics to stderr.
using System;
using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;

[ComImport, Guid("72A22D78-CDE4-431D-B8CC-843A71199B6D"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IActivationOperation {
    [PreserveSig] int GetActivateResult(out int result, [MarshalAs(UnmanagedType.IUnknown)] out object audio);
}
[Guid("41D949AB-9862-444A-80F6-C261334DA5EB"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface ICompletion {
    [PreserveSig] int ActivateCompleted(IActivationOperation operation);
}
[Guid("94EA2B94-E9CC-49E0-C0FF-EE64CA8F5B90"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAgileMarker { }
[ComVisible(true), ClassInterface(ClassInterfaceType.None)]
public sealed class Completion : ICompletion, IAgileMarker {
    public readonly ManualResetEvent Done = new ManualResetEvent(false);
    public object Audio;
    public int Result = unchecked((int)0x80004005);
    public int ActivateCompleted(IActivationOperation operation) {
        try { int hr; object audio; int call = operation.GetActivateResult(out hr,out audio);
            Result = call < 0 ? call : hr; Audio = audio;
        } catch (Exception e) { Result = Marshal.GetHRForException(e); }
        finally { Done.Set(); }
        return 0;
    }
}
[ComImport, Guid("1CB9AD4C-DBFA-4C32-B178-C2F568A703B2"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioClient {
    [PreserveSig] int Initialize(int mode,uint flags,long duration,long period,IntPtr format,IntPtr session);
    [PreserveSig] int GetBufferSize(out uint frames);
    [PreserveSig] int GetStreamLatency(out long latency);
    [PreserveSig] int GetCurrentPadding(out uint frames);
    [PreserveSig] int IsFormatSupported(int mode,IntPtr format,out IntPtr closest);
    [PreserveSig] int GetMixFormat(out IntPtr format);
    [PreserveSig] int GetDevicePeriod(out long normal,out long minimum);
    [PreserveSig] int Start();
    [PreserveSig] int Stop();
    [PreserveSig] int Reset();
    [PreserveSig] int SetEventHandle(IntPtr handle);
    [PreserveSig] int GetService(ref Guid iid,[MarshalAs(UnmanagedType.IUnknown)] out object service);
}
[ComImport, Guid("C8ADBD64-E71E-48A0-A4DE-185C395CD317"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface ICaptureClient {
    [PreserveSig] int GetBuffer(out IntPtr data,out uint frames,out uint flags,out ulong position,out ulong qpc);
    [PreserveSig] int ReleaseBuffer(uint frames);
    [PreserveSig] int GetNextPacketSize(out uint frames);
}
[StructLayout(LayoutKind.Sequential,Pack=2)]
public struct WaveFormat {
    public ushort tag,channels; public uint rate,bytesPerSecond;
    public ushort blockAlign,bits,extra;
}
[StructLayout(LayoutKind.Explicit,Size=24)]
public struct PropVariant {
    [FieldOffset(0)] public ushort vt;
    [FieldOffset(8)] public uint size;
    [FieldOffset(16)] public IntPtr blob;
}
public static class ProcessAudio {
    [DllImport("Mmdevapi.dll",CharSet=CharSet.Unicode,ExactSpelling=true)]
    static extern int ActivateAudioInterfaceAsync(string device,ref Guid iid,ref PropVariant parameters,
                                                 ICompletion handler,out IActivationOperation operation);
    static void Check(int hr) { if(hr<0) Marshal.ThrowExceptionForHR(hr); }
    [MTAThread]
    public static int Main(string[] args) {
        IntPtr blob=IntPtr.Zero,format=IntPtr.Zero;
        IAudioClient client=null; object captureObject=null; IActivationOperation operation=null;
        try {
            if(args.Length<1 || args.Length>2) throw new ArgumentException("Expected target process ID and optional parent ID.");
            uint pid=uint.Parse(args[0]); if(pid==0) throw new ArgumentException("Invalid PID.");
            Process parent=args.Length==2 ? Process.GetProcessById(int.Parse(args[1])) : null;
            // AUDIOCLIENT_ACTIVATION_PARAMS: PROCESS_LOOPBACK, PID, INCLUDE_TARGET_PROCESS_TREE.
            blob=Marshal.AllocHGlobal(12);
            Marshal.WriteInt32(blob,0,1); Marshal.WriteInt32(blob,4,unchecked((int)pid)); Marshal.WriteInt32(blob,8,0);
            PropVariant parameters=new PropVariant {vt=65,size=12,blob=blob};
            Guid iid=new Guid("1CB9AD4C-DBFA-4C32-B178-C2F568A703B2");
            Completion completion=new Completion();
            Check(ActivateAudioInterfaceAsync("VAD\\Process_Loopback",ref iid,ref parameters,completion,out operation));
            if(!completion.Done.WaitOne(10000)) throw new TimeoutException("WoW audio activation timed out.");
            Check(completion.Result); client=(IAudioClient)completion.Audio;
            WaveFormat wf=new WaveFormat {tag=1,channels=2,rate=48000,bytesPerSecond=192000,blockAlign=4,bits=16,extra=0};
            format=Marshal.AllocHGlobal(Marshal.SizeOf(typeof(WaveFormat))); Marshal.StructureToPtr(wf,format,false);
            // Shared loopback, event callback, PCM conversion. No audio endpoint changes.
            Check(client.Initialize(0,0x00020000|0x00040000|0x80000000,0,0,format,IntPtr.Zero));
            using(AutoResetEvent audioEvent=new AutoResetEvent(false)) {
                Check(client.SetEventHandle(audioEvent.SafeWaitHandle.DangerousGetHandle()));
                Guid captureId=new Guid("C8ADBD64-E71E-48A0-A4DE-185C395CD317");
                Check(client.GetService(ref captureId,out captureObject)); ICaptureClient capture=(ICaptureClient)captureObject;
                Stream output=Console.OpenStandardOutput();
                byte[] header=new byte[]{(byte)'W',(byte)'P',(byte)'C',(byte)'M',0x80,0xBB,0,0,2,0,0,0};
                output.Write(header,0,header.Length); output.Flush(); Check(client.Start());
                byte[] buffer=new byte[192000];
                for(;;) {
                    audioEvent.WaitOne(100);
                    if(parent!=null && parent.HasExited) break;
                    uint available; Check(capture.GetNextPacketSize(out available));
                    while(available>0) {
                        IntPtr data; uint frames,flags; ulong position,qpc;
                        Check(capture.GetBuffer(out data,out frames,out flags,out position,out qpc));
                        try {
                            int count=checked((int)frames*4);
                            if(buffer.Length<count) buffer=new byte[count];
                            if((flags&2)!=0) Array.Clear(buffer,0,count); else Marshal.Copy(data,buffer,0,count);
                            // A discontinuity resets downstream recognition instead of replaying a backlog.
                            if((flags&1)!=0) Console.Error.WriteLine("Audio discontinuity.");
                            output.Write(buffer,0,count); output.Flush();
                        } finally { Check(capture.ReleaseBuffer(frames)); }
                        Check(capture.GetNextPacketSize(out available));
                    }
                }
            }
            return 0;
        } catch(Exception e) {
            Console.Error.WriteLine(e.GetType().Name+": "+e.Message+" (0x"+Marshal.GetHRForException(e).ToString("X8")+")");
            return 1;
        } finally {
            if(client!=null) { try {client.Stop();} catch {} }
            if(captureObject!=null && Marshal.IsComObject(captureObject)) Marshal.ReleaseComObject(captureObject);
            if(client!=null && Marshal.IsComObject(client)) Marshal.ReleaseComObject(client);
            if(operation!=null && Marshal.IsComObject(operation)) Marshal.ReleaseComObject(operation);
            if(format!=IntPtr.Zero) Marshal.FreeHGlobal(format);
            if(blob!=IntPtr.Zero) Marshal.FreeHGlobal(blob);
        }
    }
}
