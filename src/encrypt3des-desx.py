from bitarray import bitarray

sBox = [[3,11,4,10,9,12,5,2],[15,15,1,0,0,8,13,10],[2,6,13,8,5,14,4,7],[7,9,11,3,12,14,1,6]]

shiftCounter = [4,9,10,2,11,15,3,6,13,5,0,8,12,7,14,1]

pBox = [35,50,1,62,59,8,27,53,34,57,16,46,2,41,43,29,60,44,25,10,31,49,5,30,63,12,54,22,64,37,7,47,26,4,32,51,42,11,24,61,18,40,21,28,55,14,17,23,36,9,19,20,15,52,33,3,48,58,13,45,56,39,38,6]
pBoxInv = [3,13,56,34,23,64,31,6,50,20,38,26,59,46,53,11,47,41,51,52,43,28,48,39,19,33,7,44,16,24,21,35,55,9,1,49,30,63,62,42,14,37,15,18,60,12,32,57,22,2,36,54,8,27,45,61,10,58,5,17,40,4,25,29]
xBoxLeft = [19,31,38,14,53,51,18,29,43,4,6,64,23,47,34,49,62,21,56,36,26,15,45,58,25,59,1,44,16,30,57,35,61,7,20,32,33,63,17,12]
xBoxRight = [8,48,24,41,17,33,55,14,50,5,57,2,19,20,32,29,36,10,34,46,21,27,56,12,54,52,3,9,44,22,45,11,60,37,42,15,39,40,28,64]

# plaintext = "10011111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111101"
key = "10000000000000000000000000011111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"

def makeBit(str, n):
    tmp = ""
    for i in range(0, n-len(str)):
        tmp += "0"
    return tmp + str

def intToBin(x):
    tmp = ""
    while(x>1):
        tmp =  str(x%2) + tmp
        x//=2
    tmp = str(x%2) + tmp
    return tmp
    

def substitution(bit):
    count = len(bit)//5
    ret = bitarray()
    for i in range(0, count):
        outer = int(bit[i*5])*2 + int(bit[i*5+4])
        inner = int(bit[i*5+1])*4 + int(bit[i*5+2])*2 + int(bit[i*5+3])
        ret += bitarray(makeBit(intToBin(sBox[outer][inner]),4))
    return ret


def perm(bit, box):
    tmp = []
    for i in range(0,len(box)):
        tmp.append(bit[box[i]-1])
    return tmp

def expansion(bit, key):
    one = key.count(1) % 4
    zero = key.count(0) % 4
    leftIndex = 3
    rightIndex = 4
    leftBorder = 1
    rightBorder = 14
    odd = True
    ret = []
    for i in range(0, 8):
        for j in range(0,8):
            ret.append(bit[i*8+j])
            if(odd):
                if(j==leftIndex-zero or j==rightIndex+zero):
                    ret.append(bit[i*8+j])
            else:
                if(j==leftIndex-one or j==rightIndex+one):
                    ret.append(bit[i*8+j])
        odd = not(odd)
    return bitarray(ret)

def shiftLeft(bit, counter):
    diff = abs(bit.count(1) - bit.count(0)) + shiftCounter[counter]
    tmp = bitarray(makeBit(bit[:diff].to01(),len(bit)))
    return bit<<diff | tmp
    
def mergeKey(left_key, right_key):
    return bitarray(perm(left_key, xBoxLeft)) + bitarray(perm(right_key, xBoxRight))
    

def split(bit):
    left = perm(bit[:64],pBox)
    right = perm(bit[64:],pBox)
    return (bitarray(left), bitarray(right))

def unite(left_bit, right_bit):
    left = perm(left_bit, pBoxInv)
    right = perm(right_bit, pBoxInv)
    return (bitarray(left)+ bitarray(right))

#encrypt
def encrypt(plaintext, key):
    print("encrypt")
    plain_bit = bitarray(makeBit(plaintext,128))
    key_bit = bitarray(makeBit(key,128))
    (left_plain, right_plain) = split(plain_bit)
    (left_key, right_key) = split(key_bit)

    for i in range(0,16):
        #sub-key generator
        left_key = shiftLeft(left_key, i)
        right_key = shiftLeft(right_key, i)
        sub_key = mergeKey(left_key, right_key)
        
        #saving right plain
        tmp = right_plain

        #fungsi f
        right_plain = expansion(right_plain, sub_key) ^ sub_key
        right_plain = substitution(right_plain)
        right_plain = bitarray(perm(right_plain, pBox))
        
        #feistel
        right_plain = left_plain ^ right_plain
        left_plain = tmp

    cipher = unite(left_plain, right_plain)
    return cipher

def decrypt(ciphertext, key):
    print("decrypt")
    (left_cipher, right_cipher) = split(ciphertext)
    key_bit = bitarray(makeBit(key,128))
    (left_key, right_key) = split(key_bit)
    sub_key = []

    #sub-key generator
    for i in range(0,16):
        left_key = shiftLeft(left_key, i)
        right_key = shiftLeft(right_key, i)
        sub_key.append(mergeKey(left_key, right_key))

    for i in range(16,0,-1):
        #saving left cipher
        tmp = left_cipher

        #fungsi f
        left_cipher = expansion(left_cipher, sub_key[i-1]) ^ sub_key[i-1]
        left_cipher = substitution(left_cipher)
        left_cipher = bitarray(perm(left_cipher, pBox))
        
        #feistel
        left_cipher = left_cipher ^ right_cipher
        right_cipher = tmp
    plain = unite(left_cipher, right_cipher)
    return plain

def hex2bin(s):
    mp = {'0': "0000",
          '1': "0001",
          '2': "0010",
          '3': "0011",
          '4': "0100",
          '5': "0101",
          '6': "0110",
          '7': "0111",
          '8': "1000",
          '9': "1001",
          'A': "1010",
          'B': "1011",
          'C': "1100",
          'D': "1101",
          'E': "1110",
          'F': "1111"}
    bin = ""
    for i in range(len(s)):
        bin = bin + mp[s[i]]
    return bin
 
# Binary to hexadecimal conversion
 
 
def bin2hex(s):
    mp = {"0000": '0',
          "0001": '1',
          "0010": '2',
          "0011": '3',
          "0100": '4',
          "0101": '5',
          "0110": '6',
          "0111": '7',
          "1000": '8',
          "1001": '9',
          "1010": 'A',
          "1011": 'B',
          "1100": 'C',
          "1101": 'D',
          "1110": 'E',
          "1111": 'F'}
    hex = ""
    for i in range(0, len(s), 4):
        ch = ""
        ch = ch + s[i]
        ch = ch + s[i + 1]
        ch = ch + s[i + 2]
        ch = ch + s[i + 3]
        hex = hex + mp[ch]
 
    return hex

plain_hex = "0123456789ABCDEF0123456789ABCDEF"
plaintext = hex2bin(plain_hex)
key_bit = bitarray(makeBit(key,128))
#key whitening
key_white1_b = shiftLeft(key_bit,1)
key_white2_b = shiftLeft(key_bit,3)

#key cipher first & second
key_first = shiftLeft(key_bit,2)
key_first = key_first.to01()
key_second = shiftLeft(key_bit,4)
key_second = key_second.to01()


# Start Encrypt Plaintext
print("Start Enkripsi")
print(bitarray(plaintext))
print(plain_hex)
plain_bit = bitarray(makeBit(plaintext,128))

#First key whitening
plain_whitened = plain_bit ^ key_white1_b
#first encrypt using key cipher 1
cipher = encrypt(plain_whitened.to01(), key_first)
#second decrypt using key cipher 2
cipher = decrypt(cipher, key_second)
#third encrypt using key cipher 1
cipher = encrypt(cipher.to01(), key_first)

#Second key whitening
cipher_whitened = cipher ^ key_white2_b
cipher_result = cipher_whitened.to01()
print("Hasil Enkripsi:")
print(cipher_result)
print(bin2hex(cipher_result))

# Start Decrypt Cyphertext
print("Start Dekripsi")

#Second key unwhitening
cipher_unwhitened = cipher_whitened ^ key_white2_b

#first decrypt using key cipher 1
plain = decrypt(cipher_unwhitened, key_first)
#second encrypt using key cipher 2
plain = encrypt(plain.to01(), key_second)
#third decrypt using key cipher 1
plain = decrypt(plain, key_first)

#First key unwhitening
plain = plain ^ key_white1_b

print("Hasil Dekripsi:")
print(plain.to01())
print(bin2hex(plain.to01()))