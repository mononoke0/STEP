#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
from common import format_tour, read_input

import solver_tsp

#複数の経路から最短のものを探す
def find_min_distance(tour_list, N, cities):
    distance_list = []
    for tour in tour_list:
        path_length = sum(solver_tsp.distance(cities[tour[i]], cities[tour[(i + 1)%N]])
                              for i in range(N))
        distance_list.append(path_length)

    assert len(tour_list)==len(distance_list)
    min_index = distance_list.index(min(distance_list))

    return tour_list[min_index], distance_list

def making_scatters(func_list, x, y):
    #x, y：Nの値が〜の時の分布

    assert len(func_list)==4
    list_x = []
    list_y = []
    for i in range(4):
        list_x.append(func_list[i][x])
        list_y.append(func_list[i][y])

    #関数ごとに点の色を変える
    color_code = ["#bc8f8f", "#add8e6", "#8fbc8f", "#708090"]
    name = ["inverse proportion", "exponential function", "proportional function", "constant function" ]
    n = [5, 8, 16, 64, 128, 512, 2048]
    for i in range(len(list_x)):
        plt.scatter(list_x[i], list_y[i], c = color_code[i] , label = name[i])
    plt.legend(("inverse proportion", "exponential function", "proportional function", "constant function" ),loc="lower right").get_frame().set_alpha(0.6)
    
    plt.xlabel(f'N ={n[x]}'  )
    plt.ylabel(f'N = {n[y]}')    
    plt.show()

#solverやinput.txtの数を受け取り、短い経路を探す
def generate_sample_output(CHALLENGES, COUNT, func):
    tour_list_whole =[]
    n = [5, 8, 16, 64, 128, 512, 2048]
    for i in range(CHALLENGES):
        print("searching for shortest path when N = ...", n[i])
        cities = read_input(f'input_{i}.csv')
        solver = solver_tsp

        #COUNT回だけ経路を探して、その中から最小値を求める
        tour_list = []
        for j in range(COUNT):
            print("searching path ", j+1,"th...")
            temp_tour = solver.solve(cities, func)
            tour_list.append(temp_tour)
        
        assert len(tour_list)==COUNT
        tour, distance_list = find_min_distance(tour_list, len(cities), cities)
        assert len(tour)==len(cities)+1
        tour_list_whole.append(distance_list)
     
        with open(f'output_{i}.csv', 'w') as f:
            f.write(format_tour(tour) + '\n')

    assert len(tour_list_whole)==CHALLENGES

    return tour_list_whole


#出力ファイルを読み込み、その経路の距離を出力する
def verify_output(CHALLENGE):
    for challenge_number in range(CHALLENGES):
        print(f'Challenge {challenge_number}')
        cities = read_input(f'input_{challenge_number}.csv')
        N = len(cities)
        output_prefix = 'output'
        output_file = f'{output_prefix}_{challenge_number}.csv'

        with open(output_file) as f:
                lines = f.readlines()
                assert lines[0].strip() == 'index'
                tour = [int(i.strip()) for i in lines[1:N + 1]]
        assert set(tour) == set(range(N))
        path_length = sum(solver_tsp.distance(cities[tour[i]], cities[tour[(i + 1) % N]])
                              for i in range(N))
        
        print(f'{output_prefix:16}: {path_length:>10.2f}')

    return path_length




if __name__ == '__main__':
    assert len(sys.argv)>2
    #入力ファイルの種類の数
    CHALLENGES = int(sys.argv[1])
    
    #何回経路を探すか
    COUNT = int(sys.argv[2])
    
    check = input("making a scatter? please input (Yes:y, No:n)")
    if check == "n":
        func = input("please input (inverse proportion:0, exponential function:1,\
                     proportional function:2  , constant function:3 ")
        tour_list_whole = generate_sample_output(CHALLENGES, COUNT, int(func))
        verify_output(CHALLENGES)

    elif check == "y":
        func_list = []
        for i in range(4):
            tour_list_whole = generate_sample_output(CHALLENGES, COUNT, i)
            func_list.append(tour_list_whole)
        verify_output(CHALLENGES)
        print("Making a scatter. please enter x \
            \n( N=5 -> x:0, N=8 -> x:1, N=64 -> x:2, N=128 -> x:4, N=512 -> x:5, N=2048 -> x:6 ")
        x = input()
        x = int(x)
        print("Making a scatter. please enter y \
            \n( N=5 -> y:0, N=8 -> y:1, N=64 -> y:2, N=128 -> y:4, N=512 -> y:5, N=2048 -> y:6 ")
        y = input()
        y = int(y)
        making_scatters(func_list, x, y)

    else:
        print("please input(Yes:y, No:n) ")

    
    

    
    
    
    
