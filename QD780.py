import sys,os
import time

import serial

timing_map    = {"720x480i@59.94Hz"     : "480i29",
                 "720x480i@60.00Hz"     : "480i30",
                 "720x480i@120.00Hz"    : "480i60",
                 "720x480p@59.94Hz"     : "480p59",
                 "720x480p@60.00Hz"     : "480p60",
                 "720x576i@50.00Hz"     : "576i25",
                 "720x576i@100.00Hz"    : "576i50",
                 "720x576p@50.00Hz"     : "576p50",
                 "1280x720p@23.97Hz"    : "720p23",
                 "1280x720p@24.00Hz"    : "720p24",
                 "1280x720p@25.00Hz"    : "720p25",
                 "1280x720p@29.97Hz"    : "720p29",
                 "1280x720p@30.00Hz"    : "720p30",
                 "1280x720p@50.00Hz"    : "720p50",
                 "1280x720p@59.94Hz"    : "720p59",
                 "1280x720p@60.00Hz"    : "720p60",
                 "1920x1080i@50.00Hz"   : "1080i25",
                 "1920x1080i@59.94Hz"   : "1080i29",
                 "1920x1080i@60.00Hz"   : "1080i30",
                 "1920x1080i@100.00Hz"  : "1080i50",
                 "1920x1080i@120.00Hz"  : "1080i60",
                 "1920x1080p@23.97Hz"   : "1080p23",
                 "1920x1080p@24.00Hz"   : "1080p24",
                 "1920x1080p@25.00Hz"   : "1080p25",
                 "1920x1080p@29.97Hz"   : "1080p29",
                 "1920x1080p@30.00Hz"   : "1080p30",
                 "1920x1080p@50.00Hz"   : "1080p50",
                 "1920x1080p@59.94Hz"   : "1080p59",
                 "1920x1080p@60.00Hz"   : "1080p60",
                 "3840x2160p@23.97Hz"   : "2160p23",
                 "3840x2160p@24.00Hz"   : "2160p24",
                 "3840x2160p@25.00Hz"   : "2160p25",
                 "3840x2160p@29.97Hz"   : "2160p29",
                 "3840x2160p@30.00Hz"   : "2160p30",
                 "3840x2160p@50.00Hz"   : "2160p50",
                 "3840x2160p@59.94Hz"   : "2160p59",
                 "3840x2160p@60.00Hz"   : "2160p60",
                 "640x480@60.00Hz"      : "640x480_60Hz",
                 "640x480@75.00Hz"      : "640x480_75Hz",
                 "800x600@60.00Hz"      : "800x600_60Hz",
                 "800x600@72.00Hz"      : "800x600_72Hz",
                 "800x600@75.00Hz"      : "800x600_75Hz",
                 "1024x768@60.00Hz"     : "1024x768_60Hz",
                 "1024x768@70.00Hz"     : "1024x768_70Hz",
                 "1024x768@75.00Hz"     : "1024x768_75Hz",
                 "1024x768@85.00Hz"     : "1024x768_85Hz",
                 "1280x768@60.00Hz"     : "1280x768_60Hz",
                 "1280x768@75.00Hz"     : "1280x768_75Hz",
                 "1280x768@85.00Hz"     : "1280x768_85Hz",
                 "1280x960@60.00Hz"     : "1280x960_60Hz",
                 "1280x960@85.00Hz"     : "1280x960_85Hz",
                 "1360x768@60.00Hz"     : "1360x768_60Hz",
                 "1152x864@75.00Hz"     : "1152x864_75Hz",
                 "1280x1024@60.00Hz"    : "1280x1024_60Hz",
                 "1280x1024@75.00Hz"    : "1280x1024_75Hz",
                 "1280x1024@85.00Hz"    : "1280x1024_85Hz",
                 "1680x1050@60.00Hz"    : "1680x1050_60Hz",
                 "1680x1050@85.00Hz"    : "1680x1050_85Hz",
                 "1920x1080@60.00Hz"    : "1920x1080_60Hz",
                }


class QD780_Control(object):
    """
    """
    __command_prefix__ = 'R:\> '

    def __init__(self,serial_port='COM1',baudrate=115200,cmd_retry_time=10):
        """
        Class init
        Input: For serial: serial_port([Windows]COM1/COM2/COM3/[Linux]/dev/tty...)
        """
        self.QD780_serial           = serial.Serial()
        self.QD780_serial.port      = serial_port
        self.QD780_serial.baudrate  = baudrate
        self.QD780_serial.timeout   = 1  #0.1
        self.QD780_serial.bytesize  = serial.EIGHTBITS
        self.QD780_serial.parity    = serial.PARITY_NONE
        self.QD780_serial.stopbits  = serial.STOPBITS_ONE
        self.QD780_serial.xonxoff   = 0
        self.__cmd_retry_time       = cmd_retry_time
        try:
            self.QD780_serial.open()
            self.QD780_serial.write('\n')
        except Exception as e:
            raise Exception(str(e))
        if not self.QD780_serial.isOpen():
            raise Exception('['+os.path.basename(__file__)+']['+sys._getframe().f_code.co_name+'] Fail to open '+str(serial_port))

    def __del__(self):
        self.QD780_serial.close()

    def __flush_all__(self):
        self.QD780_serial.flush()
        self.QD780_serial.flushInput()
        self.QD780_serial.flushOutput()

    def wait_console(self,timeout = 10):
        self.__flush_all__()
        self.QD780_serial.write('\n')
        start_time = time.time()
        while True:
            time.sleep(0.01)
            buffer_size = self.QD780_serial.inWaiting()
            if buffer_size > 0:
                buffer_data = self.QD780_serial.read(buffer_size)
                if buffer_data.find(self.__command_prefix__) != -1:
                    self.__flush_all__()
                    return True
            if time.time() - start_time > timeout:
                self.__flush_all__()
                return False

    def write(self,cmd):
        assert isinstance(cmd,str)
        self.__flush_all__()
        self.QD780_serial.write(cmd+'\n')
        self.__flush_all__()
        self.wait_console()

    def read(self,cmd,timeout=10):
        assert isinstance(cmd,str)
        self.__flush_all__()
        self.QD780_serial.write(cmd+'\n')
        last_buffer_size = 0
        buffer_data = ''
        start_time = time.time()
        while True:
            time.sleep(0.01)
            buffer_size = self.QD780_serial.inWaiting()
            if buffer_size > 0 and buffer_size != last_buffer_size:
                buffer_data = buffer_data + self.QD780_serial.read(buffer_size)
                if buffer_data.find(cmd) != -1:
                    temp1 = buffer_data[buffer_data.find(cmd)+len(cmd):]
                    if temp1.find(self.__command_prefix__) > 4:
                        result_data = temp1[2:temp1.find(self.__command_prefix__)-2]
                        return result_data
            last_buffer_size = buffer_size
            if time.time() - start_time > timeout:
                self.__flush_all__()
                return False

    def set_interface(self,arg = 'HDMI'):
        """
        Switch QD780 output interface
        Input: HDMI/DVI_VESA/DVI_EIA/VGA/YCbCr
        Output: True/False
        """
        assert isinstance(arg,str)
        assert arg.upper() in ('HDMI', 'DVI_VESA', 'DVI_EIA', 'VGA', 'YCBCR', 'COMPONENT')

        for retry_time in xrange(self.__cmd_retry_time):
            if arg.upper() == 'HDMI':
                self.write('XVSI 4')
                res = self.read('XVSI?')
                if res == '4':
                    return True

            elif arg.upper() == 'DVI_VESA':
                self.write('XVSI 2')
                res = self.read('XVSI?')
                if res == '2':
                    return True

            elif arg.upper() == 'DVI_EIA':
                self.write('XVSI 3')
                res = self.read('XVSI?')
                if res == '3':
                    return True

            elif arg.upper() == 'VGA':
                self.write('XVSI 9')
                self.write('AVST 2')
                self.write('SSST 1')
                res1 = self.read('XVSI?')
                res2 = self.read('AVST?')
                res3 = self.read('SSST?')
                res = (res1,res2,res3)
                if res1 == '9' and res2 == '2' and res3 == '1':
                    return True

            elif arg.upper() == 'YCBCR' or arg == 'COMPONENT':
                self.write('XVSI 9')
                self.write('AVST 6')
                self.write('SSST 3')
                res1 = self.read('XVSI?')
                res2 = self.read('AVST?')
                res3 = self.read('SSST?')
                res = (res1, res2, res3)
                if res1 == '9' and res2 == '6' and res3 == '3':
                    return True

        return False

    def set_resolution(self, arg='1080p60'):
        """
        Set Resolution on QD780
        Input: resoluton, such as 480p50
        Output: True/False
        """
        assert isinstance(arg, str)
        for retry_time in xrange(self.__cmd_retry_time):
            self.write('FMTL '+arg)
            self.write('FMTU')
            res = self.read('FMTL?')
            if res == arg:
                return True

        return False

    def set_video_bit(self, arg=8):
        """
        Set Bit Depth of video from QD780
        Input: arg (8/10/12)
        Output: True / False
        """
        assert isinstance(arg, str) or isinstance(arg, int)
        __common_sleep__ = 1.5
        for retry_time in xrange(self.__cmd_retry_time):
            self.write('NBPC '+str(arg))
            self.write('FMTU')
            res = self.read('NBPC?')
            if res == str(arg):
                return True
        return False

    def set_color_space(self, arg='YUV422'):
        """
        Set Color Space on QD780
        Input: Color Space, such as YUV422/YUV444/RGB444/YUV420
        Output: True/False
        Limitation: Currently, YUV420 only support 3840x2160p50/60 timing
        """
        assert isinstance(arg, str) and arg in ('YUV422', 'YUV444', 'RGB444', 'YUV420')
        for retry_time in xrange(self.__cmd_retry_time):
            if arg == 'YUV422':
                self.write('DVST 14')
                self.write('DVSM 2')
                self.write('ALLU')
                res1 = self.read('DVST?')
                res2 = self.read('DVSM?')
                if res1 == '14' and res2 == '2':
                    return True

            elif arg == 'YUV444':
                self.write('DVST 14')
                self.write('DVSM 4')
                self.write('ALLU')
                res1 = self.read('DVST?')
                res2 = self.read('DVSM?')
                if res1 == '14' and res2 == '4':
                    return True

            elif arg == 'YUV420':
                return False  # YUV420 only support 3840x2160p50/60 timing

            elif arg == 'RGB444':
                self.write('DVST 10')
                self.write('DVSM 0')
                self.write('ALLU')
                res1 = self.read('DVST?')
                res2 = self.read('DVSM?')
                if res1 == '10' and res2 == '0':
                    return True

        return False

    def set_pattern(self, arg = 'PGCwrgb'):
        """
        Switch QD780 output pattern
        Input: pattern
        Output: True/False
        Pattern List: SMPTEBar  |  Regulate  |  Flat_Yel
                      H_Stair   |  Checker   |  Flat_Blk
                      Pluge     |  Focus     |  Crosshtch
                      Needle    |  Multibrst |  Anmorphic
                      HiLoTrk   |  SplitGray |  GrayBar
                      Overscan  |  LG_V_CBAR |  Staircase
                      Window1   |  LG_H_CBAR |  PulseBar
                      Window2   |  V_3BARS   |  Rev_Grid
                      Raster    |  Flat_Wht  |  Linearity
                      DecodAdj  |  Flat_Red  |  PRN24Bit
                      DecodChk  |  Flat_Grn  |  ZonePlate
                      ColorBar  |  Flat_Blu  |  User01
                      Ramp      |  Flat_Cyn  |  AuxTest
                      Converge  |  Flat_Mag  |  PGCwrgb
        """
        assert isinstance(arg,str)
        pattern_list=('SMPTEBar','Regulate', 'Flat_Yel',
                      'H_Stair', 'Checker',  'Flat_Blk',
                      'Pluge',   'Focus',    'Crosshtch',
                      'Needle',  'Multibrst','Anmorphic',
                      'HiLoTrk', 'SplitGray','GrayBar',
                      'Overscan','LG_V_CBAR','Staircase',
                      'Window1', 'LG_H_CBAR','PulseBar',
                      'Window2', 'V_3BARS',  'Rev_Grid',
                      'Raster',  'Flat_Wht', 'Linearity',
                      'DecodAdj','Flat_Red', 'PRN24Bit',
                      'DecodChk','Flat_Grn', 'ZonePlate',
                      'ColorBar','Flat_Blu', 'AuxTest',
                      'Ramp',    'Flat_Cyn', 'PGCwrgb',
                      'Converge','Flat_Mag')
        for retry_time in xrange(self.__cmd_retry_time):
            self.write('IMGL '+arg)
            self.write('IMGU')
            res = self.read('IMGU?')
            if res == False:
                continue
            elif res.lower() == arg.lower():
                return True
            elif arg == 'Anmorphic' and res == 'Crosshtch':
                return True
            elif arg in ('PulseBar','Rev_Grid') and res == 'Linearity':
                return True
            elif arg in ('Checker','GrayBar','Staircase') and res == 'H_Stair':
                return True
            elif arg in ('Flat_Blk','Flat_Wht','Flat_Red','Flat_Grn','Flat_Blu','Flat_Cyn','Flat_Mag') and res == 'Flat':
                return True
            elif arg == 'AuxTest':
                return True
            elif arg not in pattern_list:
                return True

        return False

    def read_edid(self):
        """
        Read EDID, return RAW Data
        Like below:
        00FFFFFFFFFFFF00593A04100101010100180103806E3E782A97DDA45651A1240A474AA5CE0001010101010101010101010101010101023A801871382D40582C450047684200001E641900404100263018883600476842000018000000FC0045353030692D42310A20202020000000FD00384C1F500F000A20202020202001A70203217149010607020305900420260907071507508301000067030C001000001E023A801871382D40582C450047684200001E011D007251D01E206E28550047684200001E8C0AA01451F01600267C430047684200009800000000000000000000000000000000000000000000000000000000000000000000000000000000C9
        """
        for retry_time in xrange(self.__cmd_retry_time):
            res = self.read('EDID?')
            if res != False:
                return res
        return False

    def read_hdcp(self):
        """
        Read HDCP, return True(Pass)/False(Fail)
        """
        for retry_time in xrange(self.__cmd_retry_time):
            res = self.read('HDCP?')
            if res == '0':
                return True
            elif res == '1':
                return False
        return False

    def avmute_QD780(self, arg = 0):
        """
        Set AVMute on QD780
        Input: 0(Disable) / 1(Enable)
        Output: True/False
        """
        if   arg in (0,'0',False,'Disable'): set = '0'
        elif arg in (1,'1',True ,'Enable' ): set = '1'
        for retry_time in xrange(self.__cmd_retry_time):
            self.write('AVMG '+set)
            return True
        return False
