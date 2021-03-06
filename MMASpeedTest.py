import argparse
import ctypes
import time
import torch
import numpy as np

# parse cmd input args
parser = argparse.ArgumentParser()
parser.add_argument('-s', dest='size', help="both dimension size in matrix")
args = parser.parse_args()

def sumMatrix2DPyGPU(A_dev, B_dev, C_dev, nx, ny):
    nx_c = ctypes.c_int(nx)
    ny_c = ctypes.c_int(ny)
    a_p = ctypes.cast(A_dev.data_ptr(), ctypes.c_void_p)
    b_p = ctypes.cast(B_dev.data_ptr(), ctypes.c_void_p)
    c_p = ctypes.cast(C_dev.data_ptr(), ctypes.c_void_p)
    lib.sumMatrix2DGPU.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.sumMatrix2DGPU(c_p, a_p, b_p, nx_c, ny_c)


if __name__ == '__main__':

    # some basic settings, must init device in python
    torch.cuda.init()
    cuda0 = torch.device('cuda:0')
    if (args.size is None):
        nx = 1024;
        ny = 1024;
    else: 
        nx = int(args.size)
        ny = int(args.size)
    size = nx * ny;
    print(f"Comparing matrix calculation with size: {nx}x{ny}")

    # initialize tensors in CPU
    A_host = torch.ones(nx, ny, dtype=torch.float32, device='cpu')
    B_host = torch.ones(nx, ny, dtype=torch.float32, device='cpu')
    C_host = torch.zeros(nx, ny, dtype=torch.float32, device='cpu')

    # test CPU matrix addition time
    start = time.time()
    C_host = A_host + B_host
    duration = time.time() - start
    print(f"CPU matrix addition in PyTorch costs {duration:.6f} seconds")

    # initialize tensors in GPU
    A_dev = torch.ones(nx, ny, dtype=torch.float, device=cuda0)
    B_dev = torch.ones(nx, ny, dtype=torch.float, device=cuda0)
    C_dev = torch.zeros(nx, ny, dtype=torch.float, device=cuda0)
    
    # test GPU matrix addition time
    start = time.time()
    ll = ctypes.cdll.LoadLibrary
    lib = ll('./sum_matrix.so')
    sumMatrix2DPyGPU(A_dev, B_dev, C_dev, nx, ny)
    duration = time.time() - start
    print(f"GPU matrix addition in calling C costs {duration:.6f} seconds")
    
    # free GPU memory 
    # not really needed coz it is PyTorch's concern to do memory management, just trust PyTorch
    # torch.cuda.reset_accumulated_memory_stats() 