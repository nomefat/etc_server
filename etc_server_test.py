import socketserver
import struct
import time
import datetime
import threading
import os

server_port = 40009


class MyTcpHandle(socketserver.StreamRequestHandler):
    crc16_table = [
	0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
	0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
	0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
	0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
	0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
	0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
	0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
	0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
	0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
	0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
	0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
	0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
	0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
	0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
	0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
	0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
	0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
	0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
	0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
	0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
	0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
	0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
	0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
	0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
	0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
	0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
	0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
	0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
	0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
	0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
	0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
	0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
    ]
    n1_id = {}
    print_enable = 1

    
    def __init__(self,request,client_address,server):
        self.data = bytes()
        self.apid = 0
        super(MyTcpHandle, self).__init__(request,client_address,server)

        
    @staticmethod                                
    def crc(data):
        crc_value = 0
        for i in range(len(data)):
            crc_value = ((crc_value&0xffff)>>8)^MyTcpHandle.crc16_table[(crc_value^data[i])&0xff]
        return crc_value
    
    def handle(self):

        n1_id = 0

        while True:
            try:
                data0 = self.request.recv(4096)
            except Exception as ext:
                try:
                    MyTcpHandle.n1_id[str_n1id]['link'] = 0
                    print(time.ctime(),'%08X 已经下线' % self.apid, ext)
                    self.request.close()
                    #del MyTcpHandle.client_dict['%08X' % self.apid]
                except:
                    pass
                break
            else:
                if not data0:
                    try:
                        MyTcpHandle.n1_id[str_n1id]['link'] = 0
                        print(time.ctime(),'%08X 已经下线' % self.apid)
                        self.request.close()
                        #del MyTcpHandle.client_dict['%08X' % self.apid]
                    except Exception as ext:
                        pass
                    break
                self.data += data0

                cmd_head = 0
                while len(self.data) >= 18:
                    cmd_head, n1id, ip,cmd_lengh,seq = struct.unpack('<IIIHB', self.data[0:15])
                    if cmd_head != 0x584daaaa:
                        self.data = self.data[1:]
                        continue
                    
                    if len(self.data) >= 18:
                        nb_list = bytes()
                        
                        cmd_head, n1id, ip,cmd_lengh,seq,cmd1= struct.unpack('<IIIHBB', self.data[0:16])

                        file_name = time.strftime('%Y-%m-%d-%H.txt',time.localtime(time.time()))
                        timer_file_name = time.strftime('%Y-%m-%d.txt',time.localtime(time.time()))
                        str_n1id = '%04X' % n1id
                        self.apid = n1id
                        dir_name = "SDATA/%s/%s/" % (str_n1id,time.strftime('%Y-%m-%d',time.localtime(time.time())))
                        if os.path.isdir(dir_name) is False:
                            os.makedirs(dir_name)
                        if str_n1id in MyTcpHandle.n1_id:  #存在列表中 更新链接
                            MyTcpHandle.n1_id[str_n1id]['link'] = self.request
                        else:
                            MyTcpHandle.n1_id[str_n1id] = {}
                            MyTcpHandle.n1_id[str_n1id]['link'] = self.request
                            MyTcpHandle.n1_id[str_n1id]['real_file'] = open(dir_name+str_n1id + '-' + file_name,'a+')
                            MyTcpHandle.n1_id[str_n1id]['timer_file'] = open(dir_name+str_n1id + '-' + timer_file_name,'a+')
                            MyTcpHandle.n1_id[str_n1id]['down_firm'] = [bytes(),'',0,0]
                            MyTcpHandle.n1_id[str_n1id]['sensor'] = [0,0,0,0,0,0,0]

                        if dir_name+str_n1id + '-' + file_name != MyTcpHandle.n1_id[str_n1id]['real_file'].name:
                            MyTcpHandle.n1_id[str_n1id]['real_file'] = open(dir_name+str_n1id + '-' + file_name,'a+')

                        if dir_name+str_n1id + '-' + timer_file_name != MyTcpHandle.n1_id[str_n1id]['timer_file'].name:
                            MyTcpHandle.n1_id[str_n1id]['timer_file'] = open(dir_name+str_n1id + '-' + timer_file_name,'a+')                            
                            
                        self.data = self.data[15:]
                        #if MyTcpHandle.print_enable:
                         #   print('head:',n1id,cmd_lengh)
                        if cmd1 == 0xfe:
                            cmd1,cmd2,N1ID = struct.unpack('<BBI', self.data[0:6])
                            MyTcpHandle.n1_id[str_n1id]['sensor'][0] = '%04X'%N1ID
                            print('beefbeef 连接')
                        if cmd1 == 0x87:
                            cmd1,cmd2,timer_data_count = struct.unpack('BBB', self.data[0:3])
                            if MyTcpHandle.print_enable:
                                print('定时流量=%d' % timer_data_count)
                            timer_data = []
                            for i in range(timer_data_count):
                                timer_data.append(self.data[3+i*198:3+(i+1)*198])
                                
                                number,systime,datatime,gpsn,gpse = struct.unpack('<IIIff', timer_data[i][0:20])
                                write_data = '[%f-%f]%s->%s:' % (gpsn,gpse,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(datatime)))
                                MyTcpHandle.n1_id[str_n1id]['timer_file'].write(write_data)
                                for j in range(7):
                                    sid,sv,rssi,all_p,lost_p,resend_p,car,on_rate,volgate,sensor_rev_rssi,n1,n2,n3 = struct.unpack('<HHbHHHHBBbBBI', timer_data[i][44+j*22:44+(j+1)*22])
                                    str_data = '%04X %d %03d %03d:%03d %03d %03d %03d %03d %03d    ' % ( sid,sv,volgate*2,rssi,sensor_rev_rssi,all_p,lost_p,resend_p,car,on_rate)
                                    MyTcpHandle.n1_id[str_n1id]['timer_file'].write(str_data)

                                MyTcpHandle.n1_id[str_n1id]['timer_file'].write('\n')
                                MyTcpHandle.n1_id[str_n1id]['timer_file'].flush()
                                nb_list += timer_data[i][0:4]
                                if MyTcpHandle.print_enable:
                                    print('定时流量%d:->%d' % (i,number))
                            data2 = struct.pack('<IIIHBBB',0X584DAAAA,0,0,2+timer_data_count*4,0,0x87,1)
                            data2 = data2 + nb_list
                            crc_value = MyTcpHandle.crc(data2[4:])
                            data2 += bytes([(crc_value>>8) & 0xff,crc_value & 0xff])
                            self.request.sendall(data2)
                            self.data = self.data[cmd_lengh+2:]

                            
                        elif cmd1 == 0x88:
                            cmd1,cmd2,realtime_data_count = struct.unpack('BBB', self.data[0:3])
                            if MyTcpHandle.print_enable:
                                print('实时流量=%d' % realtime_data_count)
                            realtime_data = []
                            str_d = ''
                            for i in range(realtime_data_count):
                                realtime_data.append(self.data[3+i*19:3+(i+1)*19])
                                try:
                                    sid,number,sys_time,data_time,postion,ontime = struct.unpack('<HIIIBI', realtime_data[i][0:19])
                                except Exception as ext:
                                    if MyTcpHandle.print_enable:
                                        print('error:',i,)
                                    continue
                                MyTcpHandle.n1_id[str_n1id]['sensor'][postion&0x0f] = '%04X'%sid
                                nb_list += realtime_data[i][2:6]
                                if 'BEEFBEEF' in MyTcpHandle.n1_id.keys():
                                    if MyTcpHandle.n1_id['BEEFBEEF']['sensor'][0] == str_n1id and MyTcpHandle.n1_id['BEEFBEEF']['link']!=0:
                                        try:
                                            MyTcpHandle.n1_id['BEEFBEEF']['link'].sendall(struct.pack('<I',0xbeefbeef) + realtime_data[i][0:19])
                                        except Exception as ext:
                                            print('error:',i,)
                                        print('beefbeef 发送数据','%04X'%sid)
                                        
                                if postion & 0xf0 == 0:
                                    str_d += '实时流量%d:%04X->%d    ' % (i,sid,number)
                                    write_data = '[off]SID=%04X_%d NO.=%d sys_time=%s car_time=%s ON_time=%d秒:%d毫秒\n' % (sid,postion&0x0f,number,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sys_time)),
                                                                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data_time)),int(ontime/1000),ontime%1000)
                                    
                                else:
                                    try:
                                        sid,number,sys_time,data_time,postion,s_seq,resend_times,event = struct.unpack('<HIIIBBBH', realtime_data[i][0:19])
                                    except Exception as ext:
                                        if MyTcpHandle.print_enable:
                                            print('error:',i,)
                                        continue
                                    write_data = '[on]SID=%04X_%d NO.=%d sys_time=%s car_time=%s ON_event=%d秒:%d毫秒 seq=%d resend_times=%d\n' % (sid,postion&0x0f,number,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sys_time)),
                                                                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data_time)),(event>>10)&0x1f,event&0x3ff,s_seq,resend_times)

                                    
                                MyTcpHandle.n1_id[str_n1id]['real_file'].write(write_data)
                                
                            if MyTcpHandle.print_enable:
                                print(str_d)
                            MyTcpHandle.n1_id[str_n1id]['real_file'].flush()
                            
                            data2 = struct.pack('<IIIHBBB',0X584DAAAA,0,0,2+realtime_data_count*4,0,0x88,1)
                            data2 = data2 + nb_list
                            crc_value = MyTcpHandle.crc(data2[4:])
                            data2 += bytes([(crc_value>>8) & 0xff,crc_value & 0xff])                            
                            self.request.sendall(data2)

                            self.data = self.data[cmd_lengh+2:]
            
                        elif cmd1 == 0x84:
                            cmd1,cmd2,cmd3,packet_num,packet_seq = struct.unpack('<BBBHH', self.data[0:7])
                            file_name = self.data[7:-2]
                            if packet_seq > MyTcpHandle.n1_id[str_n1id]['down_firm'][2]:
                                break
                            MyTcpHandle.n1_id[str_n1id]['down_firm'][3] = packet_seq
                            if len(MyTcpHandle.n1_id[str_n1id]['down_firm'][0][(packet_seq-1)*1024:])>=1024:
                                data = MyTcpHandle.n1_id[str_n1id]['down_firm'][0][(packet_seq-1)*1024:packet_seq*1024]
                            else:
                                data = MyTcpHandle.n1_id[str_n1id]['down_firm'][0][(packet_seq-1)*1024:]
                                
                            data2 = struct.pack('<IIIHBBBBHH',0X584DAAAA,0,0,len(data)+7,0,0x84,1,0XA0,MyTcpHandle.n1_id[str_n1id]['down_firm'][2],MyTcpHandle.n1_id[str_n1id]['down_firm'][3])
                            
                            data2 = data2 + data
                            crc_value = MyTcpHandle.crc(data2[4:])
                            data2 += bytes([(crc_value>>8) & 0xff,crc_value & 0xff])
                            self.request.sendall(data2)
                            self.data = self.data[cmd_lengh+2:]
                            if MyTcpHandle.print_enable:
                                print('下载固件 总包数%d 当前包数%d'%(MyTcpHandle.n1_id[str_n1id]['down_firm'][2],MyTcpHandle.n1_id[str_n1id]['down_firm'][3]))



                        elif cmd1 == 0x86:
                            cmd1,cmd2,sys_time,id1,p1,id2,p2,id3,p3,id4,p4,id5,p5,id6,p6,id7,p7, = struct.unpack('<BBIHBHBHBHBHBHBHB', self.data[0:27])
                            if MyTcpHandle.print_enable:                            
                                if id1:
                                    print('S_[%04X] 升级进度%d' % (id1,p1))
                                if id2:
                                    print('S_[%04X] 升级进度%d' % (id2,p2))
                                if id3:
                                    print('S_[%04X] 升级进度%d' % (id3,p3))                                
                                if id4:
                                    print('S_[%04X] 升级进度%d' % (id4,p4))
                                if id5:
                                    print('S_[%04X] 升级进度%d' % (id5,p5))
                                if id6:
                                    print('S_[%04X] 升级进度%d' % (id6,p6))
                                if id7:
                                    print('S_[%04X] 升级进度%d' % (id7,p7))                                

                            self.data = self.data[cmd_lengh+2:]

                        elif cmd1 == 0x83:
                            cmd1,cmd2 =  struct.unpack('BB',self.data[0:2])
                            if cmd2 == 0x01:
                                MyTcpHandle.n1_id[str_n1id]['cfg'] = self.data[0:cmd_lengh]
                                cmd1,cmd2,crc,sys_time,n1_v,sensor_v,sensor_num,ip1_0,ip1_1,ip1_2,ip1_3,ip2_0,ip2_1,ip2_2,ip2_3,port1,port2,data_save_time,real_switch= struct.unpack('<BBHIBHBBBBBBBBBHHHB', self.data[0:27])
                                
                                print('N1_%s V=%d S_V=%d ip1[%d.%d.%d.%d port:%d] ip2[%d.%d.%d.%d port:%d] data_save_time=%d real_on_sw:%d real_off_sw:%d' % (str_n1id,n1_v,sensor_v,
                                                                                ip1_0,ip1_1,ip1_2,ip1_3,port1,ip2_0,ip2_1,ip2_2,ip2_3,port2,data_save_time,(real_switch>>4),(real_switch&0x0f)))

                                for i in range(7):
                                    s_id,off_to_on_min_t_ms,d1,d2 = struct.unpack('<HHIH', self.data[100+27+i*10:100+27+(i+1)*10])
                                    print('%04X:%dms' % (s_id,off_to_on_min_t_ms))
                            elif cmd2 == 0x02:
                                cmd11,cmd22,crc1 = struct.unpack('<BBH',MyTcpHandle.n1_id[str_n1id]['cfg'][0:4])
                                cmd1,cmd2,crc =  struct.unpack('<BBH',self.data[0:4])
                                print('N1_%s 写参数返回crc=%d:%d' % (str_n1id,crc1,crc))
                            self.data = self.data[cmd_lengh+2:]

                                
def start_down_firm(str_n1id,file_name):

    MyTcpHandle.n1_id[str_n1id]['down_firm'][0] = open(file_name,'rb').read()
    MyTcpHandle.n1_id[str_n1id]['down_firm'][1] = file_name 
    str_len = len(file_name)
    MyTcpHandle.n1_id[str_n1id]['down_firm'][2] = int(len(MyTcpHandle.n1_id[str_n1id]['down_firm'][0])/1024)
    if len(MyTcpHandle.n1_id[str_n1id]['down_firm'][0])%1024 > 0:
        MyTcpHandle.n1_id[str_n1id]['down_firm'][2] += 1
    MyTcpHandle.n1_id[str_n1id]['down_firm'][3] = 0    
    data2 = struct.pack('<IIIHBBBBHH',0X584DAAAA,0,0,str_len+7+2,0,0x84,1,0XA0,MyTcpHandle.n1_id[str_n1id]['down_firm'][2],MyTcpHandle.n1_id[str_n1id]['down_firm'][3])

    crc_value = MyTcpHandle.crc(MyTcpHandle.n1_id[str_n1id]['down_firm'][0])
    data2 = data2 + bytes([(crc_value>>8) & 0xff,crc_value & 0xff])+file_name.encode()
    crc_value = MyTcpHandle.crc(data2[4:])
    data2 += bytes([(crc_value>>8) & 0xff,crc_value & 0xff])
    MyTcpHandle.n1_id[str_n1id]['link'].sendall(data2)
    print('开始下载文件：',MyTcpHandle.n1_id[str_n1id]['down_firm'][1],'长度=%d'%MyTcpHandle.n1_id[str_n1id]['down_firm'][2])
    MyTcpHandle.print_enable = 1


def start_updata_sensor(str_n1id,id_list):
    sensor_id_list = bytes()
    print(id_list)
    try:
        for s in id_list:
            sensor_id_list += struct.pack('<H',int(s,16))
            
        data2 = struct.pack('<IIIHBBBB',0X584DAAAA,0,0,len(sensor_id_list)+3,0,0x85,1,int(len(sensor_id_list)/2))
        data2 += sensor_id_list
        crc_value = MyTcpHandle.crc(data2[4:])
        data2 += bytes([(crc_value>>8) & 0xff,crc_value & 0xff])
        MyTcpHandle.n1_id[str_n1id]['link'].sendall(data2)
        print('开始升级sensor：',id_list)
        MyTcpHandle.print_enable = 1
    except Exception as ext:
        print('升级指令错误',ext)
        
def start_adjust_sensor(str_n1id,id_list):
    sensor_id_list = bytes()
    print(id_list)
    try:
        for s in id_list:
            sensor_id_list += struct.pack('<H',int(s,16))
            
        data2 = struct.pack('<IIIHBBBB',0X584DAAAA,0,0,len(sensor_id_list)+3,0,0xa0,1,int(len(sensor_id_list)/2))
        data2 += sensor_id_list
        crc_value = MyTcpHandle.crc(data2[4:])
        data2 += bytes([(crc_value>>8) & 0xff,crc_value & 0xff])
        MyTcpHandle.n1_id[str_n1id]['link'].sendall(data2)
        print('下发校准命令：',id_list)
        MyTcpHandle.print_enable = 1
    except Exception as ext:
        print('校准指令错误',ext)

def read_cfg(str_n1id):
    
        data2 = struct.pack('<IIIHBBB',0X584DAAAA,0,0,2,0,0x83,1)
        crc_value = MyTcpHandle.crc(data2[4:])
        data2 += bytes([(crc_value>>8) & 0xff,crc_value & 0xff])
        try:
            MyTcpHandle.n1_id[str_n1id]['link'].sendall(data2)
            print('读参数N1=：',str_n1id)
        except:
            print("读N1_%08X参数错误",str_n1id)




str_help = '''********************************************************************************
    版本：0.1
    功能：ETC服务器
    操作指令：
    1.输入 ？ 返回帮助信息
    
    2.输入 ls 返回已经连接的N1ID
    
    3.输入 down n1id 选择下载固件

    4. 输入 updata n1id sensor_id1 ...  启动升级sensor 可以输入多个sensorid

    5.输入 readcfg n1id 读取N1参数 显示存储的固件版本号
    
    6.输入 openprint 会打印N1上传数据信息

    7.输入 closeprint 会关闭打印信息

    8.输入 setsf[n1id] [index] [delay ms]  设置输入索引位置的sensor的分车阈值

    9.输入 setid [n1id] [index] [sensorid]  设置输入索引位置的sensor id

********************************************************************************
'''


        
    
class CmdThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global str_help
        while True:
            str_cmd = input('>>')

            if str_cmd == '':
                continue
            
            str_cmd_list = str_cmd.split(' ')
            
            if str_cmd == 'ls':
                for key in MyTcpHandle.n1_id:
                    if MyTcpHandle.n1_id[key]['link'] != 0:
                        print('已经连接的N1:',key,MyTcpHandle.n1_id[key]['sensor'])             
            if str_cmd == '?':
                print(str_help)
            if str_cmd == 'openprint':
                MyTcpHandle.print_enable = 1
                print('打开打印信息')
            if str_cmd == 'closeprint':
                MyTcpHandle.print_enable = 0                
                print('关闭打印信息')
            if str_cmd_list[0] == 'down':
                if len(str_cmd_list) < 2:
                    print('输入N1ID')
                    continue
                list_name = []
                index = 0
                for file in os.listdir(os.getcwd()):   
                    if os.path.splitext(file)[1]=='.bin':  
                        list_name.append(file)
                        print('[%d]->%s'%(index,file))
                        index += 1
                    
                choose = int(input('>>'))
                if choose < len(list_name) and str_cmd_list[1].upper() in MyTcpHandle.n1_id:
                    start_down_firm(str_cmd_list[1].upper(),list_name[choose])
                else:
                    print('选择错误 没有这个N1 或者文件索引错误')
            if str_cmd_list[0] == 'updata':
                if len(str_cmd_list) < 3:
                    print('输入N1ID')
                    continue                
                start_updata_sensor(str_cmd_list[1].upper(),str_cmd_list[2:])
            if str_cmd_list[0] == 'adjust':
                if len(str_cmd_list) < 3:
                    print('输入N1ID')
                    continue                
                start_adjust_sensor(str_cmd_list[1].upper(),str_cmd_list[2:])                
            if str_cmd_list[0] == 'readcfg':
                if len(str_cmd_list) < 2:
                    print('输入N1ID')
                    continue
                if str_cmd_list[1].upper() in MyTcpHandle.n1_id:
                    read_cfg(str_cmd_list[1].upper())
                else:
                    print('选择错误 没有这个N1 或者文件索引错误')
            if str_cmd_list[0] == 'setsf':
                try:
                    if 'cfg'  not in MyTcpHandle.n1_id[str_cmd_list[1].upper()] or len(MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg']) < 175:
                        print('先读一下参数 才能设置')
                        continue
                except Exception as ext:
                    print(ext)
                try:
                    index = int(str_cmd_list[2])
                    if index > 6:
                        print('索引超出范围 0-6')
                        continue
                    f_ms = struct.pack('<H',int(str_cmd_list[3]))
                    
                    MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'] = MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'][0:100+27+index*10+2] + f_ms + MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'][100+27+index*10+4:]
                    
                    
                    cmd1,cmd2,crc,sys_time,n1_v,sensor_v,sensor_num,ip1_0,ip1_1,ip1_2,ip1_3,ip2_0,ip2_1,ip2_2,ip2_3,port1,port2,data_save_time,real_switch= struct.unpack('<BBHIBHBBBBBBBBBHHHB', MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'][0:27])
                    print('参数变为：')        
                    print('N1_%s V=%d S_V=%d ip1[%d.%d.%d.%d port:%d] ip2[%d.%d.%d.%d port:%d] data_save_time=%d real_on_sw:%d real_off_sw:%d' % (str_cmd_list[1].upper(),n1_v,sensor_v,
                                                                            ip1_0,ip1_1,ip1_2,ip1_3,port1,ip2_0,ip2_1,ip2_2,ip2_3,port2,data_save_time,(real_switch>>4),(real_switch&0x0f)))

                    for i in range(7):
                        s_id,off_to_on_min_t_ms,d1,d2 = struct.unpack('<HHIH', MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'][100+27+i*10:100+27+(i+1)*10])
                        print('%04X:%dms' % (s_id,off_to_on_min_t_ms))
                    print('******************************************')
                except Exception as ext:
                    print('setsf',ext)
            if str_cmd_list[0] == 'setid':
                try:
                    if 'cfg'  not in MyTcpHandle.n1_id[str_cmd_list[1].upper()] or len(MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg']) < 175:
                        print('先读一下参数 才能设置')
                        continue
                except Exception as ext:
                    print(ext)
                try:
                    index = int(str_cmd_list[2])
                    if index > 6:
                        print('索引超出范围 0-6')
                        continue
                    sid = struct.pack('<H',int(str_cmd_list[3],16))
                    
                    MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'] = MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'][0:100+27+index*10] + sid + MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'][100+27+index*10+2:]
                    
                    
                    cmd1,cmd2,crc,sys_time,n1_v,sensor_v,sensor_num,ip1_0,ip1_1,ip1_2,ip1_3,ip2_0,ip2_1,ip2_2,ip2_3,port1,port2,data_save_time,real_switch= struct.unpack('<BBHIBHBBBBBBBBBHHHB', MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'][0:27])
                    print('参数变为：')        
                    print('N1_%s V=%d S_V=%d ip1[%d.%d.%d.%d port:%d] ip2[%d.%d.%d.%d port:%d] data_save_time=%d real_on_sw:%d real_off_sw:%d' % (str_cmd_list[1].upper(),n1_v,sensor_v,
                                                                            ip1_0,ip1_1,ip1_2,ip1_3,port1,ip2_0,ip2_1,ip2_2,ip2_3,port2,data_save_time,(real_switch>>4),(real_switch&0x0f)))

                    for i in range(7):
                        s_id,off_to_on_min_t_ms,d1,d2 = struct.unpack('<HHIH', MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'][100+27+i*10:100+27+(i+1)*10])
                        print('%04X:%dms' % (s_id,off_to_on_min_t_ms))
                    print('******************************************')
                except Exception as ext:
                    print('setid',ext)
            if str_cmd_list[0] == 'downcfg':
                try:
                    if 'cfg'  not in MyTcpHandle.n1_id[str_cmd_list[1].upper()] or len(MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg']) < 175:
                        print('先读一下参数 才能设置')
                        continue
                except Exception as ext:
                    print('down_cfg0',ext)
                data = struct.pack('<IIIHBBB',0X584DAAAA,0,0,len(MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg']),0,0x83,2)                       
                data2 = MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg']
                try:
                    crc_value = MyTcpHandle.crc(data2[4:])
                    cmd = data2[0:2]
                    data2 = bytes([(crc_value>>8) & 0xff,crc_value & 0xff]) + data2[4:]
                    MyTcpHandle.n1_id[str_cmd_list[1].upper()]['cfg'] = cmd + data2
                    data1 = data + data2
                    crc_value = MyTcpHandle.crc(data1[4:])
                    data1 += bytes([(crc_value>>8) & 0xff,crc_value & 0xff])
                    MyTcpHandle.n1_id[str_cmd_list[1].upper()]['link'].sendall(data1)
                except Exception as ext:
                    print('down_cfg1',ext)
                    
                
def main():

    cmd_thread = CmdThread()
    cmd_thread.start()
    socketserver.socket.setdefaulttimeout(61*10)
    server = socketserver.ThreadingTCPServer(('0.0.0.0',server_port),MyTcpHandle)
    try:
        server.serve_forever()
    except Exception as ext:
        print('server_forever error %s' % ext)

        
if __name__ == '__main__':
    main()


