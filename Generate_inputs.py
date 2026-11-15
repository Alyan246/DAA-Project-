import os
import random

os.makedirs("datasets/karatsuba", exist_ok=True)
os.makedirs("datasets/closest_pair", exist_ok=True)

def generate_karatsuba_dataset():
    print("Generating Karatsuba datasets...")
    for i in range(1, 11):
        with open(f"datasets/karatsuba/input_{i}.txt", "w") as f:
            len1 = random.randint(150, 300)
            len2 = random.randint(150, 300)
            
            num1 = random.randint(10**(len1-1), 10**len1 - 1)
            num2 = random.randint(10**(len2-1), 10**len2 - 1)
            
            f.write(f"{num1}\n{num2}")

def generate_closestpair_dataset():
    print("Generating Closest Pair datasets...")
    for i in range(1, 11):
        with open(f"datasets/closest_pair/input_{i}.txt", "w") as f:
            num_points = random.randint(150, 500)
            
            for _ in range(num_points):
                x = random.randint(-10000, 10000)
                y = random.randint(-10000, 10000)
                f.write(f"{x},{y}\n")

