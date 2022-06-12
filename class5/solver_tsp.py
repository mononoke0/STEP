#!/usr/bin/env python3

import sys, random
import math
from sklearn.cluster import KMeans
import numpy as np
from common import print_tour, read_input


def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def function_1(N, unvisited):
    a = 0.9*((N-1)**2)/N/(N-2)
    b = 1-a
    #x：unvisited_listに含まれる要素の数
    x = unvisited
    probability = a/x/x+b

    return probability

def function_2(N, unvisited):
    a = math.log(0.1)/(N-2)
    b = -a
    x = unvisited
    probability = math.exp(a*x+b)

    return probability

def function_3(N, unvisited):
    a = 0.9/(2-N)
    b = 1-a
    probability = a*unvisited+b

    return probability

def function_4 (N, unvisited):
    probability = 0.5

    return probability

def k_means(present, unvisited_cities, clusters, cities):
    search_list = unvisited_cities+ [present]
    data = np.array([[int(cities[0][0]), int(cities[0][1])]])
    
    for i in search_list[1:]:
        x = int(cities[i][0])
        y = int(cities[i][1])
        data = np.append(data, np.array([[x, y]]), axis=0)
    #print("data size: ", data.size)
    #print("unvisited size: ", len(unvisited_cities))
    assert data.size == (len(unvisited_cities)+1)*2
    vec = KMeans(n_clusters = clusters).fit_predict(data)
    assert vec.size == (len(unvisited_cities)+1)
    candidate = []
    for i in range(vec.size-1):
        if vec[i] == vec[-1]:
            candidate.append(i)

    
    move_point = -1
    if len(candidate)>0:
        move_index = random.choice(candidate)
        move_point = search_list[move_index]
    else:
        move_point = random.choice(unvisited_cities)
    
    assert move_point > -1

    #k_means_test(present, unvisited_cities, clusters, cities, data, vec, move_point)
    
    return move_point

def k_means_test(present, unvisited_cities, clusters, cities, data, vec, move_index, move_point):
    print("[k_means_test] present city is ", present)
    print("[k_means_test] unvisited cities are" , unvisited_cities)
    print("[k_means_test] clusters: ", clusters)
    print("[k_means_test] before data: ", data)
    print("[k_means_test] clustering result ( last instance is the index of the cluster which present city belongs to ): ", vec)
    print("[k_means_test] move city number", move_point)



def annealing(dist, N, cities, func):
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]
    random.seed()
    func_list = [function_1, function_2, function_3, function_4]
    #一番近い点に移動するか、そうでないかを、unvisited_citiesに関する確率を計算する関数で決める
    while unvisited_cities:
        unvisited_cities_list = list(unvisited_cities)
        probability = func_list[func](N, len(unvisited_cities_list))
        assert probability >=0
        #unvisited cityのリストを基準のcityからの距離で小さい順に並べる
        sorted(unvisited_cities_list, key = lambda city: dist[current_city][city] )
        
        variable = random.uniform(0, 1)
        #設定した確率に含まれる場合
        if variable < probability:
            #1番近い点に移動
            next_city = unvisited_cities_list[0]
        #含まれない場合
        else:
            #k-means法で移動する点を決める
            clusters = len(unvisited_cities)//4
            if clusters == 0:
                clusters = 1
            next_city = k_means(current_city, unvisited_cities_list, clusters, cities)

        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    
    return tour

#辺を交換する関数(iから出ている辺と、j-1から出ている辺を交換する)
def swap_edge(i, j, tour):
    #print("-- swap_edge_test --")
    #print("i is ", i, ", j is ", j )
    #print(" before root is ", tour)
    new_tour = []
    new_tour.extend(tour[:i+1])
    new_tour.extend(reversed(tour[i+1:j]))
    new_tour.extend(tour[j:])
    #print("after root is", new_tour)
    #print("-- swap_edge_test end --")
    assert len(new_tour)==len(tour)
    tour = new_tour
    
    return tour, i, j
    
#辺が交差しているか確認する
def cross(i, node, dist, tour):
    if i==node:
        return False
    if i+1==node:
        return False
    #前の2本の辺の長さの合計と交換後の2本の辺の長さの合計を比較する
    before = dist[tour[i]][tour[i+1]]+dist[tour[node-1]][tour[node]]
    after = dist[tour[i]][tour[node-1]]+dist[tour[i+1]][tour[node]]

    if before > after:
        return True

    return False

#新たに辺が交換された時、その辺が既に確認ずみの点(につながる辺)の集合と交差するか確認する
#upper_i：点iより先の点について辺の交差を確認する必要がある、点0~i-1(から出る辺)は既にその他の全ての辺と交差がないことを確認済み
def recheck(node, tour, upper_i, dist):
    #既に辺の交差がないと確定している範囲に影響がないか確認
    for i in range(0, upper_i):
        #既に確定している点の集合と今調べている点の関係で場合わけする
        if (i+1 > node):
            j = i+1
            if cross(node, j, dist,tour) :
                tour, check_i, check_j = swap_edge(node, j, tour)
                upper_i = min(check_i,upper_i)
                #新たに交換した辺について交差していないか確認       
                tour, upper_i = recheck(check_i+1, tour, upper_i, dist)
                tour, upper_i = recheck(check_i+1,tour, upper_i, dist)

        #2つの辺が連結している時は交差していない              
        elif (i==node) or (i == node-1) or (i == node+1):
            continue
        else:
            j = node+1
            if cross(i, j, dist, tour) :
                tour, check_i, check_j = swap_edge(i, j, tour)   
                upper_i = min(check_i,upper_i)     

                tour, upper_i = recheck(check_i, tour, upper_i, dist)
                tour, upper_i = recheck(check_i+1,tour, upper_i, dist)
                   
    return tour, upper_i

#2-optで辺の交差をなくす関数
def check_2_opt(tour, dist):
    #基準とする点iをtourのtourの先頭ノードから(末尾のノード-2)まで動かす
    i = 0

    while i < len(tour)-2:
    #iから出ている辺と、j-1から出ている辺が交差しているか確認する    
        j = i+3
        while j < len(tour):
            if cross(i, j, dist, tour):   
                tour, check_i, check_j = swap_edge(i, j, tour)
                upper_i = min(i, check_i)
                tour, upper_i = recheck(check_i, tour, upper_i, dist)
                tour, upper_i = recheck(check_j-1, tour, upper_i, dist)
                #確定済みの点はtourリストの0番目~upper_i-1番目までに変わるので、iを更新して再び交差を調べる
                i = upper_i-1
                break
            j += 1
        i += 1

    return tour


def solve(cities, func):
    N = len(cities)
    #各点間の距離を表すリスト
    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])
    
    #で経路を求める
    tour = annealing(dist, N, cities, func)
    #最後の線で重ならないようにtourの末尾に出発点を追加
    tour.append(0) 
    #2-optで交差している辺をつなぎ直す
    tour = check_2_opt(tour, dist)
    
    return tour


if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print("------------a main id(tour): ", id(tour))
    print_tour(tour)
