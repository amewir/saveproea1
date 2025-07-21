import pyqrcode

con =1234
while con <= 1239:
    
        roster = con
        id = '71' + str(con)

        qr = pyqrcode.create(71 and id, error='L')

        qr.png('G' +str(roster) + '.png', scale=6)
        
        con += 1