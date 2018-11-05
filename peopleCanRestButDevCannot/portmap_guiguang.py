import re

sdk_port_list9 ='00 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29'.split()
snmp_port_list9 ='29 06 02 16 08 12 04 14 10 28 23 24 25 01 15 03 07 13 05 27 09 11 19 20 26 22 21 17 18'.split()
showc_port_list9='''
port   id0   id1  addr iaddr                    name    timeout
ge0(  2)   143  bff0    81    81                    65LP     250000
ge1(  3)   143  bff0    82    82                    65LP     250000
ge2(  4)   143  bff0    83    83                    65LP     250000
ge3(  5)   143  bff0    84    84                    65LP     250000
ge4(  6)   143  bff0    85    85                    65LP     250000
ge5(  7)   143  bff0    86    86                    65LP     250000
ge6(  8)   143  bff0    87    87                    65LP     250000
ge7(  9)   143  bff0    88    88                    65LP     250000
ge8( 10)   143  bff0    89    89                    65LP     250000
ge9( 11)   143  bff0    8a    8a                    65LP     250000
ge10( 12)   143  bff0    8b    8b                    65LP     250000
ge11( 13)   143  bff0    8c    8c                    65LP     250000
ge12( 14)   143  bff0    8d    8d                    65LP     250000
ge13( 15)   143  bff0    8e    8e                    65LP     250000
ge14( 16)   143  bff0    8f    8f                    65LP     250000
ge15( 17)   143  bff0    90    90                    65LP     250000
ge16( 18)   143  bff0    91    91                    65LP     250000
ge17( 19)   143  bff0    92    92                    65LP     250000
ge18( 20)   143  bff0    93    93                    65LP     250000
ge19( 21)   143  bff0    94    94                    65LP     250000
ge20( 22)   143  bff0    95    95                    65LP     250000
ge21( 23)   143  bff0    96    96                    65LP     250000
ge22( 24)   143  bff0    97    97                    65LP     250000
ge23( 25)   143  bff0    98    98                    65LP     250000
xe0( 26)    20  63f6    39    99         BCM8727_NTU_2XG     250000
xe1( 27)    20  63f6    38    9a         BCM8727_NTU_2XG     250000
xe2( 28)    20  63f6    38    9b         BCM8727_NTU_2XG     250000
xe3( 29)    20  63f6    39    9c         BCM8727_NTU_2XG     250000
'''
snmp_sdk_map9={}
sdk_bcmshell_map9={}

for i in range(len(sdk_port_list9)):
    snmp_sdk_map9[snmp_port_list9[i]]=sdk_port_list9[i]
#print(snmp_sdk_map9)

for j in showc_port_list9.split('\n'):
    #print([j])
    a=re.match('(\w+)\(\s+(\w+)\)\s+.*',j)
    if a:
        print(a.groups())
        sdk_bcmshell_map9[a.group(2)]=a.group(1)
print(sdk_bcmshell_map9)
sdk_port_list10 ='00 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29'
snmp_port_list10 ='29 06 02 16 08 12 04 14 10 28 19 20 25 01 15 03 07 13 05 27 09 11 23 24 26 18 17 21 22'
showc_port_list10='''
port   id0   id1  addr iaddr                    name    timeout
ge0(  2)   143  bff0    81    81                    65LP     250000
ge1(  3)   143  bff0    82    82                    65LP     250000
ge2(  4)   143  bff0    83    83                    65LP     250000
ge3(  5)   143  bff0    84    84                    65LP     250000
ge4(  6)   143  bff0    85    85                    65LP     250000
ge5(  7)   143  bff0    86    86                    65LP     250000
ge6(  8)   143  bff0    87    87                    65LP     250000
ge7(  9)   143  bff0    88    88                    65LP     250000
ge8( 10)   143  bff0    89    89                    65LP     250000
ge9( 11)   143  bff0    8a    8a                    65LP     250000
ge10( 12)   143  bff0    8b    8b                    65LP     250000
ge11( 13)   143  bff0    8c    8c                    65LP     250000
ge12( 14)   143  bff0    8d    8d                    65LP     250000
ge13( 15)   143  bff0    8e    8e                    65LP     250000
ge14( 16)   143  bff0    8f    8f                    65LP     250000
ge15( 17)   143  bff0    90    90                    65LP     250000
ge16( 18)   143  bff0    91    91                    65LP     250000
ge17( 19)   143  bff0    92    92                    65LP     250000
ge18( 20)   143  bff0    93    93                    65LP     250000
ge19( 21)   143  bff0    94    94                    65LP     250000
ge20( 22)   143  bff0    95    95                    65LP     250000
ge21( 23)   143  bff0    96    96                    65LP     250000
ge22( 24)   143  bff0    97    97                    65LP     250000
ge23( 25)   143  bff0    98    98                    65LP     250000
xe0( 26)    20  63f6    39    99         BCM8727_NTU_2XG     250000
xe1( 27)    20  63f6    38    9a         BCM8727_NTU_2XG     250000
xe2( 28)    20  63f6    38    9b         BCM8727_NTU_2XG     250000
xe3( 29)    20  63f6    39    9c         BCM8727_NTU_2XG     250000
'''


