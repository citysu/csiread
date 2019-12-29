"""
Split the large data file of linux-80211n-tool into small pieces
"""

import os


def csi_split(csifile, save_path, c_num=[], c_offset=[]):
    """Split the data file of linux-80211n-tool into small pieces

    csifile: raw csi data file
    save_path: path to save small pieces
    """
    cur = 0
    fpset = [0]
    with open(csifile, 'rb') as f: 
        lens = f.seek(0, os.SEEK_END)
        f.seek(0, os.SEEK_SET)
        while cur < (lens - 3):
            field_len = int.from_bytes(f.read(2), byteorder='big')    
            code = int.from_bytes(f.read(1), byteorder='little')
            cur = cur + 3
            if code == 0xbb:
                f.seek(field_len - 1, os.SEEK_CUR)
                cur = cur + field_len - 1
                fpset.append(cur)
            else:
                f.seek(field_len - 1, os.SEEK_CUR)
                cur = cur + field_len - 1
        fpset.pop()
        print('packets number: ', len(fpset))

        f.seek(0, os.SEEK_SET)
        for i, (x, y) in enumerate(zip(c_num, c_offset)):
            spath = os.path.join(save_path, '%s.dat' % (str(i).zfill(4)))
            f.seek(fpset[c_offset[i]], os.SEEK_SET)
            with open(spath, 'wb') as f2:
                f2.write(f.read(fpset[c_offset[i] + c_num[i]] - fpset[c_offset[i]]))
            print(spath)


if __name__ == "__main__":
    CSIFILE = '../material/5300/dataset/sample_0x1_ap.dat'
    SPATH = '../material/5300/dataset/sample_split/'
    C_OFFSET = [1, 2, 3, 4]
    C_NUM = [0, 1, 2, 3]

    if os.path.exists(SPATH) is False:
        os.makedirs(SPATH)
    csi_split(CSIFILE, SPATH, C_NUM, C_OFFSET)
