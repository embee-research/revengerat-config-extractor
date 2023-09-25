"""

    Basic config extractor for RevengeRat/LimeRat
    

    by Matthew @Embee_research
    
    Obtains config from files in the current directory
    
    Usage: "Revenge-config-extractor.py" (No arguments)
    

    Some portions of this code were heavily inspired by RussianPanda's WhiteSnakeStealer blog


   sha256: fa95d5e77fd4fab91662c9b1e460807647acb25769469110b59fb6485b17cc8d
   sha256: 2e0e188d4b837df3c8bbed3227493a9074e668b84a48b9dc81dacc596f23e048
   sha256: 2b89a560332bbc135735fe7f04ca44294703f3ae75fdfe8e4fc9906521fd3102
"""




import re
import clr,sys,os


clr.AddReference(os.getcwd() + "\\dnlib.dll")
import dnlib
from dnlib.DotNet import *
from dnlib.DotNet.Emit import OpCodes


def has_config_sequence(method):
    #Obtain target opcode sequence
    #This portion was heavily inspired by the RussianPanda WhiteSnakeStealer Post
    
    #Opcode Sequence 1
    target_opcode_sequence1 =  [OpCodes.Call,OpCodes.Stfld,OpCodes.Ldarg_0,OpCodes.Ldstr,OpCodes.Ldstr,OpCodes.Ldc_I4_M1,OpCodes.Ldc_I4_0,OpCodes.Call,OpCodes.Stfld,OpCodes.Ldarg_0,OpCodes.Ldstr,OpCodes.Stfld,OpCodes.Ldarg_0,OpCodes.Ldstr,OpCodes.Stfld,OpCodes.Ldarg_0,OpCodes.Ldc_I4_0,OpCodes.Stfld,OpCodes.Ldarg_0,OpCodes.Ldc_I4_0,OpCodes.Stfld,OpCodes.Ret]
    #Opcode sequence 2
    target_opcode_sequence2 =  [OpCodes.Ldstr, OpCodes.Stsfld,OpCodes.Ldstr, OpCodes.Stsfld, OpCodes.Ldstr, OpCodes.Stsfld,OpCodes.Ldstr, OpCodes.Stsfld,OpCodes.Ldstr, OpCodes.Stsfld,OpCodes.Ldstr, OpCodes.Stsfld, OpCodes.Newobj, OpCodes.Stsfld, OpCodes.Ret]

    targets = [target_opcode_sequence1,target_opcode_sequence2]
    
    #Check for both opcode sequences
    for target_opcode_sequence in targets:
        target_len = len(target_opcode_sequence)
        for i in range(target_len):
            target_opcode_sequence[i] = target_opcode_sequence[i].Name

        
        if method.HasBody:
            current_opcode_sequence = [instr.OpCode.Name for instr in method.Body.Instructions]
            for i in range(1,target_len-1):
                if target_opcode_sequence[-i] != current_opcode_sequence[-i]:
                    return False
            if set(target_opcode_sequence) <= set(current_opcode_sequence):
                #print(method.FullName)
                return True
            #print(method.FullName)

    return False
        

def get_config_values(method):
    #Obtain config values from "ldstr" opcodes
    #eg
    #IL_0000: ldstr     "marcelotatuape.ddns.net"
    config = []
    if method.HasBody:
        for instr in method.Body.Instructions:
            if instr.OpCode == OpCodes.Ldstr:
                if instr.Operand != ',':
                    config.append(instr.Operand)

    return config
                

def get_target_method(module):
    #Obtain the method that contains configuration
    for type in module.GetTypes():
        for method in type.Methods:
            if method.HasBody and has_config_sequence(method):

                return method

    return False
                
if __name__ == "__main__":
    #Try to extract configs from files in current directory
    for filename in os.listdir(os.getcwd()):
        try:
            module = dnlib.DotNet.ModuleDefMD.Load(filename)
            method = get_target_method(module)
            config = get_config_values(method)
            print(filename + " : " + str(config))
        except:
            print(filename + " : Unable to obtain config")
            pass
    

#Example of RevengeRAT Configuration being searched for
"""


		/* 0x000030FC 72E4020070   */ IL_0000: ldstr     "marcelotatuape.ddns.net"
		/* 0x00003101 800A000004   */ IL_0005: stsfld    string Lime.Settings.Config::host
		/* 0x00003106 7214030070   */ IL_000A: ldstr     "333"
		/* 0x0000310B 800B000004   */ IL_000F: stsfld    string Lime.Settings.Config::port
		/* 0x00003110 721C030070   */ IL_0014: ldstr     "TnlhbkNhdFJldmVuZ2U="
		/* 0x00003115 800C000004   */ IL_0019: stsfld    string Lime.Settings.Config::id
		/* 0x0000311A 7246030070   */ IL_001E: ldstr     "2180459765"
		/* 0x0000311F 800D000004   */ IL_0023: stsfld    string Lime.Settings.Config::currentMutex
		/* 0x00003124 725C030070   */ IL_0028: ldstr     "Revenge-RAT"
		/* 0x00003129 800E000004   */ IL_002D: stsfld    string Lime.Settings.Config::key
		/* 0x0000312E 7274030070   */ IL_0032: ldstr     "!@#%^NYAN#!@$"
		/* 0x00003133 8010000004   */ IL_0037: stsfld    string Lime.Settings.Config::splitter
		/* 0x00003138 736C00000A   */ IL_003C: newobj    instance void [System]System.Diagnostics.Stopwatch::.ctor()
		/* 0x0000313D 8011000004   */ IL_0041: stsfld    class [System]System.Diagnostics.Stopwatch Lime.Settings.Config::stopwatch
		/* 0x00003142 2A           */ IL_0046: ret




"""
