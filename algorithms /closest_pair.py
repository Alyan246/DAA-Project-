import math 

def distance(p1 , p2):
    return math.hypot(p1[0] - p2[0] , p1[1] - p2[1])

def mergesort(arr , key):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid] , key)
    right = mergesort(arr[mid:] , key)
    
    merged = []
    i = j = 0

    while i < len(left) and j <  len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i = i+1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def closest_pair(points):
    n = len(points)

    if n <= 3:
        min_dist = float('inf')
        best_pair = None
        for i in range(n):
            for j in range(i+1 , n):
                d = distance(points[i] , points[j])
                if d < min_dist:
                    min_dist = d
                    best_pair = (points[i] , points[j])

        return min_dist , best_pair

    pointsx = mergesort(points , key = lambda p:p[0])
    mid = n//2
    midpt = pointsx[mid]

    dl , pair_left = closest_pair(pointsx[:mid])
    dr , pair_right = closest_pair(pointsx[mid:])

    d = dl
    best_pair = pair_left
    if dr < dl:
        d = dr
        best_pair = pair_right

    strip = [p for p in pointsx if abs(p[0] - midpt[0]) < d]

    strip = mergesort(strip , key= lambda p: p[1])

    for i in range(len(strip)):
        for j in range(i+1 , len(strip)):
            if (strip[j][1] - strip[i][1]) >= d:
                break

            dist = distance(strip[i] , strip[j])
            if dist < d:
                d = dist
                best_pair = (strip[i] , strip[j])
    return d , best_pair

