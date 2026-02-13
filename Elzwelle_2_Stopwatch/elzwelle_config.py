import socket

# Google Spreadsheet ID for publishing times
# Elzwelle SPREADSHEET_ID = '1obtfHymwPSGoGoROUialryeGiMJ1vkEUWL_Gze_hyfk'
# FilouWelle spreadsheet_xxx, err := service.FetchSpreadsheet("1M05W0igR6stS4UBPfbe7-MFx0qoe5w6ktWAcLVCDZTE")
SPREADSHEET_ID = '1M05W0igR6stS4UBPfbe7-MFx0qoe5w6ktWAcLVCDZTE'

# Port number for the web server
PORT_NUMBER = 8080 # Maybe set this to 9000.
HOST_NAME = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
