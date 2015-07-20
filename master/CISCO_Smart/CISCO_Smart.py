# coding: utf-8

import httplib, urllib
import urllib2
import time
import json

# ˼������·�ɣ��ж����ߵ��ƶ��豸
# ��ʵ�� EA4200, EA4500, EA6500, EA6700

# ��Ҫ��ص� mac ��ַ�б�
mac_list = [ ] # ['����','CC:FA:00:F7:52:69',true,0], ['iphone','F0:CB:A1:00:77:EE',true,0] 

class CISCO :

	# �ص������豸
	def online_devices(self, func):
		global mac_list

		# �ж�ָ����ŵ� MAC �Ƿ�����
		params = "[{\"action\":\"http://linksys.com/jnap/devicelist/GetDevices\",\"request\":{\"sinceRevision\":23}},{\"action\":\"http://linksys.com/jnap/networkconnections/GetNetworkConnections\",\"request\":{}}]"
		request = urllib2.Request(url='http://192.168.1.1/JNAP/', data=params, headers={ "Content-type": "application/json; charset=UTF-8", "X-JNAP-Action": "http://linksys.com/jnap/core/Transaction" })
	
		try:
			f = urllib2.urlopen(request)
		except urllib2.HTTPError, e:
			print 'The server couldn\'t fulfill the request.'
			print 'Error code: ', e.code
			return
		except urllib2.URLError, e:
			print 'We failed to reach a server.'
			print 'Reason: ', e.reason
			return
		else:
			# ���û�������쳣
			t = f.headers["Content-type"]

			# ������ص��� json �ļ�֤���ǶԵ�
			if t.startswith("application/json;"):
				data = f.read()

			# �������ص����� ˼��·����ר�ò���
			json_list = json.loads(data)
			if json_list["result"] == "OK":
				# ��ʼ���б�
				# if len(mac_list) == 0:
				devices = [x for x in json_list["responses"][0]["output"]["devices"] if x["model"]["deviceType"] == "Mobile" or x["model"]["deviceType"] == "Phone"]
				for device in devices:
					knownMACAddresses = device["knownMACAddresses"][0]
					# ����б��д��ڼ�¼
					in_list = [x for x in mac_list if x[1] == knownMACAddresses]
					if len(in_list) > 0:
						continue

					# ��ȡ�豸����
					userDeviceName = False
					friendlyName = device["friendlyName"]		
					# ����Ǵ��ڱ������豸��������ʱ��Ҫ���쾯��
					item = [x for x in device["properties"] if x["name"] == "userDeviceName"]
					if len(item) > 0:
						friendlyName = item[0]["value"]		
						userDeviceName = True		
					# ���浽�豸�б�
					# print friendlyName, device["knownMACAddresses"][0]
					mac_item = [ friendlyName, device["knownMACAddresses"][0], userDeviceName, -1 ] 
					mac_list.append(mac_item)

				# ��ѯ mac �б��������״̬
				for element in mac_list:
					mac = element[1]			# mac ��ַ
					old_status = element[3]		# ����״̬
					new_status = 0

					# ƥ�������б� 
					# 4200
					# connection = [x for x in json_list["responses"][0]["output"]["devices"] if x["knownMACAddresses"][0] == mac and len(x["connections"]) > 0]
					# 6500
					connection = [x for x in json_list["responses"][1]["output"]["connections"] if x["macAddress"] == mac]
					if len(connection) > 0:
						new_status = 1	# ����

					# �������״̬�����仯
					if old_status != new_status:
						element[3] = new_status
						# print (old_status, new_status)
						if old_status == 0 and new_status == 1:
							# print element[0].encode("utf-8") + ' ���ˡ�'
							# �����ߣ����ţ�����ʾ�ƣ�������ʾ
							func(element[0].encode("utf-8"), element[2], new_status)
						elif old_status == 1 and new_status == 0:
							# print element[0].encode("utf-8") + ' ���ˡ�'
							# ��ʾ����
							func(element[0].encode("utf-8"), element[2], new_status)

					# print element, len(connection)

	def main():
		try:
			while True:   
				is_online()

				time.sleep(1)
		except KeyboardInterrupt:
			print('User press Ctrl+c ,exit;')
		finally:
			pass

	#if __name__ == "__main__":
	#	main()