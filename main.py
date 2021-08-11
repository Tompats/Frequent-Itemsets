import pandas as pd
import csv
import time
import os.path
import matplotlib.pyplot as plt
from itertools import combinations


#function for reading rating files and create appropriate dataframes
def ReadRatings(file):
    my_ratings_df = pd.read_csv(file)
    return my_ratings_df



#function for reading movies file and create appropriate dataframe
def ReadMovies(file):
    my_movies_df = pd.read_csv(file)
    return my_movies_df



#function to create user baskets
def CreateUserBaskets(my_ratings_df):
    #clone the dataframe
    copy_df = my_ratings_df.copy()
    all_users_movies = []
    #get a list of unique users
    unique_users = copy_df['userId'].unique()
    copy_df.set_index("userId",
              inplace = True)
    #get all movies for each user
    for userId in unique_users:
        user_movies = copy_df.loc[[userId],['movieId']].to_dict(orient='list')
        all_users_movies.append(user_movies['movieId'])
    #create a dictionary from the 2 lists
    my_userBaskets = dict(zip(unique_users, all_users_movies))
    return my_userBaskets




def CreateMovieBaskets(my_ratings_df):
    copy_df = my_ratings_df.copy()
    all_movies_users = []
    unique_movies = copy_df['movieId'].unique()
    copy_df.set_index("movieId",
              inplace = True)
    for movieId in unique_movies:
        movie_users = copy_df.loc[[movieId],['userId']].to_dict(orient='list')
        all_movies_users.append(movie_users['userId'])
    my_movieBaskets = dict(zip(unique_movies, all_movies_users))
    return my_movieBaskets




def getMovie(my_movies_df, movieId):
    copy_movies_df = my_movies_df.copy()
    movie = copy_movies_df.loc[copy_movies_df['movieId'] == movieId]
    return movie.to_string()




def getUser(my_ratings_df, userId):
    copy_users_df = my_ratings_df.copy()
    user = copy_users_df.loc[copy_users_df['userId'] == userId]
    return user.to_string()



def WriteUserBasketToCsv(my_userBaskets,file):
    with open(file, 'w') as f:
        f.write("userId,movies\n")
        for key in my_userBaskets.keys():
            f.write("%s,%s\n"%(key,my_userBaskets[key]))



def WriteMovieBasketToCsv(my_movieBaskets,file):
    with open(file, 'w') as f:
        f.write("movieId,users\n")
        for key in my_movieBaskets.keys():
            f.write("%s,%s\n"%(key,my_movieBaskets[key]))





def LoadBasket(filename):
    ids = []
    arrays = []
    with open(filename, mode='r') as inp:
        reader = csv.reader(inp)
        line_count = 0
        for row in reader:
            if line_count == 0:
                line_count += 1
            else:
                ids.append(int(row[0]))
                pp = row[1:]
                new = []
                for i in pp:
                    temp1 = i.replace('['," ")
                    temp2 = temp1.replace(']'," ")
                    new.append(int(temp2))
                arrays.append(new)
    basket = dict(zip(ids,arrays))
    return basket





def ExactCounting(itemBaskets):
    hash_table = {}
    flag = True
    k = 1
    while flag:
        for key in itemBaskets:
            #get the doubles/triples/quadraples etc. given k. I.e if k=2 we get pairs, k=3 we get triplets etc.
            combines = combinations(itemBaskets[key],k)
            #create an array of the values
            array = [i for i in combines]
            for j in array:
                if j in hash_table:
                    hash_table[j] += 1
                else:
                    hash_table[j] = 1
        if k==2:
            flag = False
        k+=1

    return hash_table





def ExactCountingToFile(exact_counting_table,file):
    f = open(file, "w")
    for i in exact_counting_table:
        f.write(str(i)+" "+str(exact_counting_table[i])+"\n")
    f.close()




def getPairs(k,array,frequents):
    new_array = []
    if k==1:
        return array
    #get pairs
    elif k==2:
        for i in array:
            if i in frequents:
                for j in array:
                    if(j>i and j in frequents):
                        new_array.append([i,j])
    #get triple/quadraples etc
    elif k>2:
        for i in array:
            if(str(i) in frequents):
                for j in array:
                    if str(j) in frequents:
                        for q in j:
                            if(q>i[-1]):
                                f = i.copy()
                                f.append(q)
                                if f not in new_array:
                                    new_array.append(f)
    return new_array











def myApriori(itemBaskets, minSupport, maxLength):
    hash_table = {}
    frequentHashTable = {}
    frequentItemSets = []
    flag = True
    k = 1
    terminate = 0
    multiples = []
    #the multiples of each basket.
    multiples_big = []
    while flag:
        counter = 0
        for key in itemBaskets:
            #print(key)
            if k==1:
                multiples.append(itemBaskets[key])
                for i in itemBaskets[key]:
                    if i in hash_table:
                        hash_table[i] += 1
                    else:
                        hash_table[i] = 1
            if k>=2:
                pairs = getPairs(k,multiples_big[-1][counter],frequentItemSets[k-2])
                multiples.append(pairs)
                #print("HI")
                for i in pairs:
                    if str(i) in hash_table:
                        hash_table[str(i)] += 1
                    else:
                        hash_table[str(i)] = 1
            counter+=1
        frequents = []

        #keep only the doubles/triple etc. that have been found at least minSupport times
        for key in hash_table:
            if hash_table[key]>=minSupport:
                frequentHashTable[key] = hash_table[key]
                terminate+=1


        frequentItemSets.append(frequentHashTable)
        hash_table = {}
        frequentHashTable = {}
        multiples_big = []
        multiples_big.append(multiples)
        multiples = []
        mul_cop = []
        print("Pass number: "+str(k)+" -> done!")
        if k==maxLength or terminate<2:
            flag = False
        k+=1
        terminate = 0
    return frequentItemSets





def myAprioriToFile(array_dict,file):
    f = open(file, "w")
    for i in array_dict :
        for j in i:
            f.write(str(j)+" "+str(i[j])+"\n")
    f.close()





def createChunks(dict, n):
    array_of_chunks = []
    chunk = {}
    counter=0
    for i in dict:
        counter+=1
        chunk[i] = dict[i]
        if counter==n:
            array_of_chunks.append(chunk)
            counter = 0
            chunk = {}
    if counter!=0:
        array_of_chunks.append(chunk)
    return array_of_chunks





def SON(itemBaskets, minSupport, maxLength, chunksSize):
    CandidateSets = []
    hash_table = {}
    frequents = {}
    frequentItemSets = []
    for i in range(maxLength):
        frequentItemSets.append({})
    number = 0
    #1st pass
    array_of_chunks = createChunks(itemBaskets,chunksSize)
    minSupport_modified = (minSupport // len(array_of_chunks))
    for chunk in array_of_chunks:
        number+=1
        print('''Apriori's passes for chunk number '''+str(number)+':')
        CandidateSets.append(myApriori(chunk,minSupport_modified,maxLength))
        print()
    #2nd pass
    n = 0
    for set in CandidateSets:
        for dict in set:
            for key in dict:
                counter=0
                if type(key) is int:
                    n = 0
                    for i in itemBaskets:
                        if key in itemBaskets[i]:
                            counter+=1
                else:
                    arr = stringArrayToInt(key)
                    n = len(arr) - 1
                    for i in itemBaskets:
                        total = 0
                        for j in arr:
                            if int(j) in itemBaskets[i]:
                                total+=1
                        if(total == len(arr)):
                            counter+=1
                if counter >= minSupport:
                    #hash_table[key] = counter
                    frequentItemSets[n][key] = counter

    #sort by keys
    #sorted_table =  {key: val for key, val in sorted(hash_table.items(), key = lambda ele: str(ele[0]))}
    return frequentItemSets




def SONtoFile(dict,file):
    f = open(file, "w")
    for i in dict :
        for j in i:
            f.write(str(j)+" "+str(i[j])+"\n")
    f.close()




def stringArrayToInt(str):
    s = str.split('[')
    ss = s[1].split(']')
    res = ss[0].split(',')
    return res



def sortDict(array_dict):
    for i in range(len(array_dict)):
        dict = array_dict[i]
        res = {key: val for key, val in sorted(dict.items(), key = lambda ele: ele[1])}
        array_dict[i] = res
    return array_dict





def countKeys(array_dict):
    count = 0
    for i in array_dict:
        count += len(i.keys())
    return count







def printHistogram(dict):
    df = pd.DataFrame(dict,columns = ['count','support'])
    df.plot(x ='support', y='count', kind = 'bar')
    plt.title('Histogram of supports for frequent itemsets')
    plt.xlabel('Support')
    plt.ylabel('Number of Frequent Itemsets')
    plt.tight_layout()
    plt.show()






def getMenu():
    line = "---------------------------------------------------------------------------------------------------"
    menu = line+"\n"+line+"\n"+"\n"
    menu += '''\t(C)\tCreate Baskets and Dataframes\t[Format: c, <u(sers),m(ovies)>, filename]\n
        (L)\tLoad Baskets from csv File\t[Format: l, <u(sers),m(ovies)>, filename]\n
        (W)\tWrite Baskets to csv File\t[Format: w, <u(sers),m(ovies)>, filename]\n
        (E)\tExact Counting\t\t\t[Format: e, <u(sers),m(ovies)>, filename]\n
        (A)\tApriori\t\t\t\t[Format: a, <u(sers),m(ovies)>, filename, minSupport, maxLength]\n
        (S)\tSON\t\t\t\t[Format: s, <u(sers),m(ovies)>, filename, minSupport, maxLength, chunksSize]\n
        (M)\tDetails For Movies\t\t[Format: m, <comma sep. movieIds>]\n
        (U)\tDetails For Users\t\t[Format: u, <comma sep. userIds>]\n
        (O)\tOrder Results\t\t\t[Format: o, <a(priori), s(on)>, filename]\n
        (P)\tPrint Histogram\t\t\t[Format: p]\n
        (Q)\tQuit\t\t\t\t[Format: q]'''
    menu += "\n\n\n"+line+"\n"+line+"\n"
    return menu





def presentResults():
    menu = getMenu()
    print(menu)
    my_userBaskets = {}
    my_movieBaskets = {}
    apriori = []
    plot_dict = {}
    counts_for_users = []
    supports_for_users = []
    counts_for_movies = []
    supports_for_movies = []
    inp = input("Make your choice: ")
    while inp != 'q' and inp != '':
        print("Please Be Patient!\n")
        format = inp.split(',')
        choice = format[0]
        if choice!= 'p':
            obj = format[1]
        #try:
        if len(format)>2:
            filename = format[2]
        #except:
            #continue
        start_time = time.time()
        if choice=='c':
            if os.path.isfile(filename):
                if obj == 'u':
                    my_ratings_df = ReadRatings(filename)
                    my_userBaskets = CreateUserBaskets(my_ratings_df)
                    my_movieBaskets = CreateMovieBaskets(my_ratings_df)
                elif obj == 'm':
                    my_movies_df = ReadMovies(filename)
            else:
                print ("File does not exist!")
        if choice=='w':
            if obj == 'u':
                WriteUserBasketToCsv(my_userBaskets,filename)
            elif obj == 'm':
                WriteMovieBasketToCsv(my_movieBaskets,filename)
        if choice=='e':
            if obj == 'u':
                exact_counting_table = ExactCounting(my_userBaskets)
                ExactCountingToFile(exact_counting_table,filename)
            elif obj == 'm':
                exact_counting_table = ExactCounting(my_movieBaskets)
                ExactCountingToFile(exact_counting_table,filename)
        if choice=='l':
            if os.path.isfile(filename):
                if obj == 'u':
                    my_userBaskets = LoadBasket(filename)
                elif obj == 'm':
                    my_movieBaskets = LoadBasket(filename)
            else:
                print ("File does not exist!")
        if choice=='a':
            minSupport = int(format[3])
            maxLength = int(format[4])
            if obj == 'u':
                apriori = myApriori(my_userBaskets, minSupport, maxLength)
                count = countKeys(apriori)
                counts_for_users.append(count)
                supports_for_users.append(minSupport)
                myAprioriToFile(apriori,filename)
            elif obj == 'm':
                apriori = myApriori(my_movieBaskets, minSupport, maxLength)
                count = countKeys(apriori)
                counts_for_movies.append(count)
                supports_for_movies.append(minSupport)
                myAprioriToFile(apriori,filename)
        if choice=='s':
            minSupport = int(format[3])
            maxLength = int(format[4])
            chunksSize = int(format[5])
            if obj == 'u':
                son = SON(my_userBaskets, minSupport, maxLength, chunksSize)
                count = countKeys(son)
                counts_for_users.append(count)
                supports_for_users.append(minSupport)
                SONtoFile(son,filename)
            elif obj == 'm':
                son = SON(my_movieBaskets, minSupport, maxLength, chunksSize)
                count = len(son.keys())
                counts_for_movies.append(count)
                supports_for_movies.append(minSupport)
                SONtoFile(son,filename)
        if choice=='m':
            #in order to get a movie please create my_movies_df first! (press c,m,"your file")
            for i in format:
                if i!= 'm':
                    try:
                        print(getMovie(my_movies_df, int(i)))
                    except:
                        print("Please Create the dataframe first!")
        if choice=='u':
            #in order to get a user please create my_ratings_df first! (press c,u,"your file")
            for i in format:
                if i!= 'u':
                    try:
                        print(getUser(my_ratings_df, int(i)))
                    except:
                        print("Please Create the dataframe first!")
        if choice=='o':
            if obj == 'a':
                try:
                    apriori_sorted = sortDict(apriori)
                    myAprioriToFile(apriori_sorted,filename)
                except:
                    print("Please execute apriori's algorithm first")
            elif obj == 's':
                try:
                    son_sorted = sortDict(son)
                    myAprioriToFile(son_sorted,filename)
                except:
                    print("Please execute son's algorithm first")
        if choice=='p':
            if obj == 'u':
                plot_dict['count'] = counts_for_users
                plot_dict['support'] = supports_for_users
                printHistogram(plot_dict)
                plot_dict_users = {}
            elif obj == 'm':
                plot_dict['count'] = counts_for_movies
                plot_dict['support'] = supports_for_movies
                printHistogram(plot_dict)
                plot_dict = {}


        end_time = time.time()
        print("\nTime: "+str(end_time-start_time)+"sec.\n")
        cont = input("Do you want to continue [Y,n]? ")
        if (cont == 'n' or cont=='no' or cont == 'No' or cont == 'N'):
            inp = 'q'
        else:
            print(menu)
            inp = input("Make your choice: ")
    print("Goodbye!")






def main():
    presentResults()




#call main function as soon as the program starts
if __name__ == '__main__':
    main()
