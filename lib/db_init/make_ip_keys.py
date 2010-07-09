#!/usr/bin/python
# -*- coding: utf-8 -*-

# copy of the fonctions designed for the whois server 

class MakeIPKeys:
    
    def __init__(self, ipv4):
        self.ipv4 = ipv4

    def intermediate_sets(self, first_set, last_set):
        intermediate = []
        if self.ipv4:
            intermediate = self.__intermediate_sets_v4(first_set, last_set)
        else:
            intermediate = self.__intermediate_sets_v6(first_set, last_set)
        return intermediate

    def __intermediate_sets_v4(self, first_set, last_set):
        intermediate = []
        first_index = first_set.split('.')
        last_index = last_set.split('.')
        if first_index[0] != last_index[0]:
            # push each values between first and last (first and last excluded) 
            intermediate = self.__intermediate_between(int(first_index[0])+ 1 , int(last_index[0]) - 1)
            if first_index[1] == '0' and last_index[1] == '255':
                intermediate.append(first_index[0])
                intermediate.append(last_index[0])
            else:
                # push each values from first_index[0].first_index[1] to first_index[0].255
                intermediate += self.__intermediate_to_last(first_index[1], first_index[0] + '.')
                # push each values from last_index[0].0 to last_index[0].last_index[1]
                intermediate += self.__intermediate_to_last(last_index[1], last_index[0] + '.')
        elif first_index[0] == last_index[0] and first_index[1] == '0' and last_index[1] == '255':
            intermediate.append(first_index[0])
        elif first_index[1] != last_index[1]:
            # push each values between first and last (first and last excluded) 
            intermediate = self.__intermediate_between(int(first_index[1])+ 1 , int(last_index[1]) - 1, first_index[0] + '.')
            if first_index[2] == '0' and last_index[2] == '255':
                intermediate.append(first_index[0] + '.' + first_index[1])
                intermediate.append(first_index[0] + '.' + last_index[1])
            else:
                # push each values from first_index[0].first_index[1].first_index[2] to first_index[0].first_index[1].255
                intermediate += self.__intermediate_to_last(first_index[2], first_index[0] + '.' + first_index[1] + '.')
                # push each values from last_index[0].last_index[1].0 to last_index[0].last_index[1].last_index[2]
                intermediate += self.__intermediate_to_last(last_index[2], last_index[0] + '.' + last_index[1] + '.')
        elif first_index[1] == last_index[1] and first_index[2] == '0' and last_index[2] == '255':
            intermediate.append(first_index[0] + '.' + first_index[1])
        elif first_index[2] != last_index[2]:
            intermediate = self.__intermediate_between(int(first_index[2]) , int(last_index[2]), first_index[0] + '.' + first_index[1] + '.')
        elif first_index[2] == last_index[2]:
            intermediate.append(first_index[0] + '.' + first_index[1] + '.' + first_index[2])
        return intermediate
    
    def __intermediate_sets_v6(self, first_set, last_set):
        intermediate = []
        first_index = first_set.split(':')
        last_index = last_set.split(':')
        i = 0
        key = ''
        while first_index[i] == last_index[i]:
            if i > 0 :
                 key += ':'
            key += first_index[i]
            i += 1
            if i == len(first_index) or i == len(last_index):
                break
        if key == '':
            if len(first_index[0]) == 0:
                first_index[0] = 0
            hex_first = int('0x' + first_index[0], 16)
            hex_last = int('0x' + last_index[0], 16)
            while hex_first <= hex_last:
                key_end = ('%X' % hex_first).lower()
                intermediate.append(key_end)
                hex_first += 1
        else:
            intermediate.append(key)
        return intermediate
    
    # push each values from first_index[0].first_index[1] to first_index[0].255
    def __intermediate_to_last(self, first, main_str = ''):
        intermediate = []
        first = int(first)
        while first <= 255:
            intermediate.append(main_str + str(first))
            first += 1
        return intermediate

    # push each values from last_index[0].0 to last_index[0].last_index[1]
    def __intermediate_from_zero(self, last, main_str = ''):
        intermediate = []
        last = int(last)
        b = 0
        while b <= last:
            intermediate.append(main_str + str(b))
            b += 1
        return intermediate
    
    def __intermediate_between(self, first, last, main_str = ''):
        intermediate = []
        while first <= last:
            intermediate.append(main_str + str(first))
            first += 1
        return intermediate

