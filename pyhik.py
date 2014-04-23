from __future__ import print_function
import ctypes,os,threading,time
from ctypes.wintypes import DWORD
from datetime import datetime

__author__ = 'gmuralit'

####################################################
### Load the dll                                 ###
####################################################
HC = ctypes.WinDLL('HCNetSDK.dll')

####################################################
### Global variables                             ###
####################################################
SERIALNO_LEN = 48
STREAM_ID_LEN = 32
__curdir__ = os.getcwd()
__capdir__ = os.path.join(__curdir__,"capture")
__logdir__ = os.path.join(__curdir__,"logs")
exitFlag = 0

####################################################
### Data types to be used in the library         ###
####################################################
BOOL = ctypes.c_bool
INT = ctypes.c_int
LONG = ctypes.c_long
BYTE = ctypes.c_ubyte
WORD = ctypes.c_ushort
CHARP = ctypes.c_char_p
VOIDP = ctypes.c_void_p
HWND = ctypes.c_uint

CMPFUNC = ctypes.WINFUNCTYPE(None,LONG,DWORD,BYTE,DWORD,VOIDP)

####################################################
### Structures to be used in the library         ###
####################################################
class NET_DVR_DEVICEINFO_V30(ctypes.Structure):
    _fields_ = [("sSerialNumber",BYTE * SERIALNO_LEN),
                ("byAlarmInPortNum",BYTE),
                ("byAlarmOutPortNum",BYTE),
                ("byDiskNum",BYTE),
                ("byDVRType",BYTE),
                ("byChanNum",BYTE),
                ("byStartChan",BYTE),
                ("byAudioChanNum",BYTE),
                ("byIPChanNum",BYTE),
                ("byZeroChanNum",BYTE),
                ("byMainProto",BYTE),
                ("bySubProto",BYTE),
                ("bySupport",BYTE),
                ("bySupport1",BYTE),
                ("bySupport2",BYTE),
                ("wDevType",WORD),
                ("bySupport3",BYTE),
                ("byMultiStreamProto",BYTE),
                ("byStartDChan",BYTE),
                ("byStartDTalkChan",BYTE),
                ("byHighDChanNum",BYTE),
                ("bySupport4",BYTE),
                ("byRes2",BYTE * 10)
                ]
LPNET_DVR_DEVICEINFO_V30 = ctypes.POINTER(NET_DVR_DEVICEINFO_V30)

class NET_DVR_CLIENTINFO(ctypes.Structure):
    _fields_ = [
                ("lChannel",LONG),
                ("lLinkMode",LONG),
                ("hPlayWnd",HWND),
                ("sMultiCastIP",CHARP),
                ("byProtoType",BYTE),
                ("byRes",BYTE*3)
                ]
LPNET_DVR_CLIENTINFO = ctypes.POINTER(NET_DVR_CLIENTINFO)

class NET_DVR_PREVIEWINFO(ctypes.Structure):
    _fields_ = [
                ("lChannel",LONG),
                ("dwStreamType",DWORD),
                ("dwLinkMode",DWORD),
                ("hPlayWnd",HWND),
                ("bBlocked",DWORD),
                ("bPassbackRecord",DWORD),
                ("byPreviewMode",BYTE),
                ("byStreamID",BYTE * STREAM_ID_LEN),
                ("byProtoType",BYTE),
                ("byRes",BYTE * 222),
                ]
LPNET_DVR_PREVIEWINFO = ctypes.POINTER(NET_DVR_PREVIEWINFO)

class NET_DVR_SDKLOCAL_CFG(ctypes.Structure):
    _fields_ = [
                ("byEnableAbilityParse",BYTE),
                ("byVoiceComMode",BYTE),
                ("byRes",BYTE*382),
                ("byProtectKey",BYTE*128)
                ]
LPNET_DVR_SDKLOCAL_CFG = ctypes.POINTER(NET_DVR_SDKLOCAL_CFG)

class NET_DVR_JPEGPARA(ctypes.Structure):
    _fields_ = [
                ("wPicSize",WORD),
                ("wPicQuality",WORD)
                ]

LPNET_DVR_JPEGPARA = ctypes.POINTER(NET_DVR_JPEGPARA)

####################################################
### Error codes                                  ###
####################################################
__errorcodes__ = {
0: 'No error',
3: 'SDK is not initialized',
7: 'Failed to connect to the device. The device is off-line, or connection timeout caused by network',
10: 'Timeout when receiving the data from the device',
12: 'API calling order error',
34: 'Failed to create a file, during local recording, saving picture, getting configuration file or downloading record file',
84: 'Load StreamTransClient.dll failed'
}

####################################################
### SDK Information functions                    ###
####################################################
def getSDKVersion():
    """
    Get SDK version information

    @Params
    None

    @Return
    SDK Version information [Call getLastError() to get the error code]
    """
    _gsv = HC.NET_DVR_GetSDKVersion
    _gsv.restype = DWORD
    return hex(_gsv())

####################################################
### SDK initialization and termination functions ###
####################################################
def init(filePtr):
    """
    Initialize the SDK. Call this function before using any of the other APIs

    @Params
    filePtr  - File pointer to the SDK log file

    @Return
    None
    """
    _init = HC.NET_DVR_Init
    _init.restype = BOOL
    if _init():
        print(str(datetime.now())+"|INFO|SDK initialized successfully",file=filePtr)
    else :
        _m=str(datetime.now())+"|ERROR|SDK initialization failed. Error message: "+getErrorMsg(getLastError())
        print(_m,file=filePtr)
        raise Exception(_m)

def release(filePtr):
    """
    Release the SDK. If init() was called, invoke this function at program exit

    @Params
    filePtr  - File pointer to the SDK log file

    @Return
    None
    """
    _release = HC.NET_DVR_Cleanup
    _release.restype = BOOL
    if _release():
        print(str(datetime.now())+"|INFO|SDK released successfully",file=filePtr)
    else :
        _m=str(datetime.now())+"|ERROR|SDK release failed. Error message: "+getErrorMsg(getLastError())
        print(_m,file=filePtr)
        raise Exception(_m)

####################################################
### Connection timeout functions                 ###
####################################################
def setConnectTime(timeout,attemptCount,filePtr):
    """
    Set network connection timeout and connection attempt times. Default timeout is 3s.

    @Params
    timeout - timeout, unit:ms, range:[300,75000]
    attemptCount - Number of attempts for connection
    filePtr  - File pointer to the SDK log file

    @Return
    None
    """
    _sct = HC.NET_DVR_SetConnectTime
    _sct.argtypes = [DWORD, DWORD]
    _sct.restype = BOOL
    if _sct(timeout,attemptCount):
        print(str(datetime.now())+"|INFO|Set connect time-"+str(timeout)+":"+str(attemptCount),file=filePtr)
    else:
        print(str(datetime.now())+"|ERROR|Set connect time failed",file=filePtr)

def setReconnect(interval,enableReconnect,filePtr):
    """
    Set reconnecting time interval. Default reconnect interval is 5 seconds.

    @Params
    interval - Reconnecting interval, unit:ms, default:30s
    enableReconnect - Enable or disable reconnect function, 0-disable, 1-enable(default)
    filePtr  - File pointer to the SDK log file

    @Return
    None
    """
    _sr = HC.NET_DVR_SetReconnect
    _sr.argtypes = [DWORD, DWORD]
    _sr.restype = BOOL
    if _sr(interval,enableReconnect):
        print(str(datetime.now())+"|INFO|Set reconnect time-"+str(interval)+":"+str(enableReconnect),file=filePtr)
    else:
        print(str(datetime.now())+"|ERROR|Set reconnect time failed",file=filePtr)

####################################################
### Error message functions                      ###
####################################################
def getLastError():
    """
    The error code of last operation

    @Params
    None

    @Return
    Error code
    """
    _gle = HC.NET_DVR_GetLastError
    _gle.restype = DWORD
    return _gle()

def getErrorMsg(errorCode):
    """
    Return the error message of last operation

    @Params
    errorCode - Error code from getLastError()

    @Return
    Error message
    """
    return __errorcodes__[errorCode]

####################################################
### Device login functions                       ###
####################################################
def login(dIP,dPort,username,password,filePtr):
    """
    Login to the device

    @Params
    dIP - IP address of the device
    dPort - Port number of the device
    username - Username for login
    password - password
    filePtr  - File pointer to the SDK log file

    @Return
    (userID, dInfo) - Unique user ID and device info, else -1 on failure [Call getLastError() to get the error code]
    """
    _l = HC.NET_DVR_Login_V30
    _l.argtypes = [CHARP,WORD,CHARP,CHARP,LPNET_DVR_DEVICEINFO_V30]
    _l.restype = LONG
    _info = NET_DVR_DEVICEINFO_V30()
    _userId = _l(dIP,dPort,username,password,ctypes.byref(_info))
    if _userId != -1:
        print(str(datetime.now())+"|INFO|Logged in successfully",file=filePtr)
        return _userId,_info
    else :
        _m = str(datetime.now())+"|INFO|Login failed. Error message: "+getErrorMsg(getLastError())
        print(_m,file=filePtr)
        raise Exception(_m)

def logout(userId,filePtr):
    """
    Logout from the device

    @Params
    userID - User ID, returned from login()
    filePtr  - File pointer to the SDK log file

    @Return
    None
    """
    _lo = HC.NET_DVR_Logout
    _lo.argtypes = [LONG]
    _lo.restype = BOOL
    _ldir = os.path.join(__logdir__,'SDK.log')
    f = open(_ldir,'a')
    if _lo(userId):
        print(str(datetime.now())+"|INFO|Logged out successfully",file=filePtr)
    else :
        _m = str(datetime.now())+"|ERROR|Logout failed. Error message: "+getErrorMsg(getLastError())
        print(_m,file=filePtr)
        raise Exception(_m)

####################################################
### Live view functions                          ###
####################################################
def startRealPlay(userId,ipClientInfo,realDataCbk,userData,blocked):
    """
    Starting live view

    @Params
    userId - return value of login()
    ipClientInfo - Live view parameter
    realDataCb - Real-time stream data callback function
    userData - User data
    blocked - Whether to set stream data requesting process blocked or not: 0-no, 1-yes

    @Return
    -1 on failure [Call getLastError() to get the error code]
    Other values - live view handle for use in stopRealPlay()
    """
    _srp = HC.NET_DVR_RealPlay_V30
    if realDataCbk:
        _srp.argtypes = [LONG,LPNET_DVR_CLIENTINFO,CMPFUNC,VOIDP,BOOL]
    else:
        _srp.argtypes = [LONG,LPNET_DVR_CLIENTINFO,VOIDP,VOIDP,BOOL]
    _srp.restype = LONG
    return _srp(userId,ctypes.byref(ipClientInfo),realDataCbk,userData,blocked)

def stopRealPlay(realHandle):
    """
    Stopping live view

    @Params
    realHandle - live view handle, return value from startRealPlay()

    @Return
    TRUE on success
    FALSE on failure [Call getLastError() to get the error code]
    """
    _strp = HC.NET_DVR_StopRealPlay
    _strp.argtypes = [LONG]
    _strp.restype = BOOL
    return _strp(realHandle)

def getRealPlayerIndex(realHandle):
    """
    Get player handle to use with other player SDK functions

    @Params
    realHandle - Live view handle, return value from startRealPlay()

    @Return
    -1 on failure [Call getLastError() to get the error code]
    Other values - live view handle
    """
    _grpi = HC.NET_DVR_GetRealPlayerIndex
    _grpi.argtypes = [LONG]
    _grpi.restype = INT
    return _grpi(realHandle)

####################################################
### Capture picture functions                    ###
####################################################

def captureJPEGPicture(userId,channelNo,jpegParam,fileName,filePtr):
    """
    Capture a frame and save to file

    @Params
    userId - User Id, return value from login()
    channelNo - Channel index for capturing the picture
    jpegParam - Target JPEG picture parameters
    fileName - URL to save picture
    filePtr - File pointer to the logfile

    @Return
    TRUE on success
    FALSE on failure [Call getLastError() to get the error code]
    """
    _cjp = HC.NET_DVR_CaptureJPEGPicture
    _cjp.argtypes = [LONG,LONG,LPNET_DVR_JPEGPARA,CHARP]
    _cjp.restype = BOOL
    if _cjp(userId,channelNo,ctypes.byref(jpegParam),fileName):
        print(str(datetime.now())+"|INFO|Picture captured successfully at "+fileName,file=filePtr)
    else:
        print(str(datetime.now())+"|ERROR|Picture capture failed. Error message: "+getErrorMsg(getLastError()),file=filePtr)


####################################################
### Callback functions                           ###
####################################################
def setRealDataCallBack(lRealHandle,cbRealDataCbk,dwUser):
    """
    Set callback function

    @Params
    lRealHandle - live view handle, return value from startRealPlay()
    cbRealDataCbk - Callback function
    dwUser - User data

    @Return
    TRUE on success
    FALSE on failure [Call getLastError() to get the error code]
    """
    _srdcb = HC.NET_DVR_SetRealDataCallBack
    _srdcb.argtypes = [LONG,CMPFUNC,DWORD]
    _srdcb.restype = BOOL
    return _srdcb(lRealHandle,cbRealDataCbk,dwUser)

####################################################
### Helper functions                             ###
####################################################
def struct2tuple(struct):
    """
    Convert a structure to a tuple

    @Params
    struct - ctypes structure object

    @Return
    Tuple containing the values of all the fields in the struct
    """
    _sf = NET_DVR_DEVICEINFO_V30._fields_
    _dict = {}
    for _fn,_ft in _sf:
        _v = struct.__getattribute__(_fn)
        if(type(_v)) != int:
            _v = ctypes.cast(_v,ctypes.c_char_p).value
        _dict[_fn] = _v
    return _dict

def logger():
    """
    Logger utility

    @Params
    None

    @Return
    None
    """
    if not os.path.exists(__logdir__):
        os.makedirs(__logdir__)
    _ldir = os.path.join(__logdir__,'SDK.log')
    f = open(_ldir,'w')
    print(str(datetime.now())+"|INFO|"+_ldir+" created",file=f)


def createDirectory(startName,count):
    """
    Creates a directory, if not exists

    @Params
    startName - starting name for the directory [numbers]
    count - count of the directories to be created

    @Return
    None
    """
    for _chan in  range(startName,count):
        _cdir = os.path.join(__capdir__,str(_chan))
        _ldir = os.path.join(__logdir__,str(_chan)+'chan.log')
        if not os.path.exists(_cdir):
            os.makedirs(_cdir)
        f = open(_ldir,'w')
        print(str(datetime.now())+"|INFO|"+_ldir+" created",file=f)

def checkVideoStatus(userId,channelNo,jpegParam):
    """
    Checks video status for the particular device, channel number and logs the information

    @Params
    userId - User Id, return value from login()
    channelNo - Channel index for capturing the picture
    jpegParam - Target JPEG picture parameters
    """
    global exitFlag
    _loop = 1
    _cdir = os.path.join(__capdir__,str(channelNo))
    _ldir = os.path.join(__logdir__,str(channelNo)+'chan.log')
    f=open(_ldir,'a')
    print(str(datetime.now())+"|INFO|Thread started for "+str(channelNo),file=f)

    while not exitFlag:
        print(str(datetime.now())+"|INFO|Thread called for "+str(channelNo),file=f)
        captureJPEGPicture(userId,channelNo,jpegParam,os.path.join(_cdir,str(channelNo)+'_'+str(_loop)+'.jpeg'),f)
        if _loop > 2:

            # Write code here for video status#

            os.remove(os.path.join(_cdir,str(channelNo)+'_'+str(_loop-2)+'.jpeg'))
        _loop+=1
        time.sleep(0.18)

    print(str(datetime.now())+"|INFO|Thread stopped for "+str(channelNo),file=f)

class CThread(threading.Thread):
    def __init__(self,threadId,name,userId,channelNo,jpegParam):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        self.userId = userId
        self.channelNo = channelNo
        self.jpegParam = jpegParam

    def run(self):
        checkVideoStatus(self.userId,self.channelNo,self.jpegParam)


####################################################
### Test functions                               ###
####################################################
def startCapture16(ip,port,username,password,duration):
    """
    Start the capture for 16 video channels of the device and log the video status for every capture

    @Params
    ip - IP address of the device
    port - Port of the device
    username - Username for login
    password - Password for login
    duration - Duration for the test run

    @Return
    None
    """
    logger()
    f = open(os.path.join(__logdir__,'SDK.log'),'a')

    init(f)
    setConnectTime(2000,2,f)
    setReconnect(100,True,f)
    userId,deviceInfo = login(ip,port,username,password,f)

    dictDeviceInfo = struct2tuple(deviceInfo)
    startChan = dictDeviceInfo['byStartChan']
    chanNum = dictDeviceInfo['byChanNum']

    createDirectory(startChan,chanNum+1)

    jpegParam = NET_DVR_JPEGPARA()
    jpegParam.wPicSize = 2
    jpegParam.wPicQuality = 2

    for threadid in range(1,17):
        thread = CThread(threadid,'Channel'+str(threadid),userId,threadid,jpegParam)
        thread.start()


    startTime = int(time.time())
    endTime = duration * 3600
    print(str(datetime.now())+"|INFO|Startime:"+str(startTime)+";ETA in "+str(endTime)+"s",file=f)

    while True:
        if int(time.time()) - startTime > endTime:
            global exitFlag
            exitFlag = 1
            break

    logout(userId,f)
    release(f)


if __name__ == "__main__":
    startCapture16("10.78.203.159",8000,"admin","12345",0.0066)