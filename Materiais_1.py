from ast import And
from email.utils import decode_rfc2231
from faulthandler import disable
import pandas as pd 
import streamlit as st
import itertools
from PIL import Image


d = {'Material':[' '], 'Descrição':[' '], 'Característica1': [' '], 'Característica2': [' ']}
r = pd.DataFrame(d)


st.image('https://seekvectorlogo.com/wp-content/uploads/2018/03/saint-gobain-vector-logo.png',width=150)
st.title('Materiais duplicados e com características diferentes')
st.sidebar.markdown("**Instruções para o usuário**")
st.sidebar.write('*Há dois tipos de análises, materiais duplicados e materiais da mesma família com carecterísticas diferentes,  \n o arquivo anexo deve mudar de acodo com a opção escolhida.  \n Para materiais duplicados o arquivo deve estar com as seguintes colunas: Material e Descrição  \n Ex.*', r[['Material','Descrição']], '*Para materiais da mesma família com características diferentes o arquivo deve estar com as seguintes colunas: Material, Descrição e Colunas com as características a serem analizadas.  \n Ex.*', r)
st.sidebar.write('*Material = Código do item; Descrição = Descrição do item ou da categoria; Características =  Parâmetro a ser analisado.  \n **Obs**.  \n As Colunas Material e Descrição precisam ser mantidas com os mesmos nomes.  \n Apenas uma característica será analizada por vez.*')

#Drag and drop in streamlit
upload = st.file_uploader("Upload a Dataset", type=['xlsx'])


if upload is not None:
    df = pd.read_excel(upload)
    r1 = dict(df)
    r2 = [' ',]
    
    for i in r1.keys():
        r2.append(i)
    # Reading the document in .xlsx (excel)
   
    r3 = len(r2)
    
                  
    def jaccard_similarity(x, y): 
        
        # List the unique words in a document
        words_x = set(x) 
        words_y = set(y)
        
        # Find the intersection of words list of x & y
        intersection = words_x.intersection(words_y)

        # Find the union of words list
        union = words_x.union(words_y)
            
        # Calculate Jaccard similarity score 
        # using length of intersection set divided by length of union set
        return float(len(intersection)) / len(union)

    run = st.button("Materiais duplicados") 
    run2 = st.button("Materiais da mesma família com características diferentes")

    Coluna = st.selectbox('Qual campo será analizado?', options = r2[3:r3+1])
    
    
     
    
    if run == True:

        # Using .lower() to let all sentences with lowercase letters, and using .split() to split each sentence in a list. 
        
        df['Descrição'] = df['Descrição'].apply(str)
        df['Material'] = df['Material'].apply(str)
        df['Descrição'] = df['Descrição'].str.lower().str.split(' ')

        # Creating a list, where each element has two objects, 1st = Description, 2sd = Material. 
        # Example: [(['broca', 'helic', 'escalonada', 'aco', '8,0', 'mmx'], '410175755-')...]

        wordings_users = list(zip(df["Descrição"], df["Material"]))

        # Creating a empty list to store the values generated in the for loop
        result1 = []

        # Defining the for loop and an itertools.combination with 2 elements, where each combination is a sublist inside the list. So the function defined at the beginnig analizes each sublist.
        for item in list(itertools.combinations(wordings_users, 2)):
            
            # Calling the function defined at the beginning. 
            similarity = jaccard_similarity(item[0][0], item[1][0])
            
            # Creating a dictonary with the for loop result. 
            data = {"Material1": item[0][1], "Descrição1": item[0][0], "Material2": item[1][1], "Descrição2": item[1][0], "Similaridade": similarity}
            
            # Storing the for loops results in the list created before. 
            result1.append(data)

            # Transforming the list in a DataFrame. 
        df1 = pd.DataFrame(result1)

        # Subset the DataFrame where the similarity is over 80%
        df2 = df1[(df1['Similaridade'] >0.8) & (df1['Similaridade'] <= 1)].sort_values('Similaridade', ascending = False)
        st.dataframe(df2)
        st.write('Numero de combinações acima de 80% de similaridade :',  len(df2.axes[0]))
        df2.to_excel('Duplicados.xlsx', index = False)

    if run2 == True:
        
        df['Descrição'] = df['Descrição'].apply(str)
        df['Material'] = df['Material'].apply(str)
        y = df.groupby(['Descrição'])[Coluna].value_counts()
        y1 = df.groupby('Descrição').count().reset_index()
        y2 = y1[['Descrição','Material']]
        y2['Descrição'] = y2['Descrição'].str.lower().str.split(' ')
       
        
        g = df.groupby(['Descrição'])[Coluna].apply(pd.Series.mode)
        g = pd.DataFrame(g)
        
        g = g.reset_index()

        
        y = pd.DataFrame(y)
        dfx = pd.merge(y, g,  how='left', on=['Descrição'])
        p = dfx.reset_index()
        c = p.groupby(['Descrição',Coluna+'_y'])[Coluna+'_x'].max()
        v = pd.DataFrame(c).reset_index()
        dfb = pd.merge(df, v,  how='left', on=['Descrição'])

        
        

        # Using .lower() to let all sentences with lowercase letters, and using .split() to split each sentence in a list. 
        dfb['Descrição'] = dfb['Descrição'].str.lower().str.split(' ')
        
        # Creating a list, where each element has two objects, 1st = Description, 2sd = Material. 
        # Example: [(['broca', 'helic', 'escalonada', 'aco', '8,0', 'mmx'], '410175755-')...]

        wordings_users = list(zip(dfb["Descrição"], dfb["Material"], dfb[Coluna].apply(str), dfb[Coluna+'_y'].apply(str), dfb[Coluna+'_x'].apply(str)))

        # Creating a empty list to store the values generated in the for loop
        result1 = []

        # Defining the for loop and an itertools.combination with 2 elements, where each combination is a sublist inside the list. So the function defined at the beginnig analizes each sublist.
        for item in list(itertools.combinations(wordings_users, 2)):
            
            # Calling the function defined at the beginning. 
            similarity = jaccard_similarity(item[0][0], item[1][0])
            
            # Creating a dictonary with the for loop result. 
            data = {"Material1": item[0][1], "Descrição1": item[0][0], Coluna+"1": item[0][2], "NCM1_indicado": item[0][3], "NCM1_FREQUENCIA": item[0][4], "Material2": item[1][1], "Descrição2": item[1][0], Coluna+"2": item[1][2],"NCM2_indicado": item[1][3], "NCM2_FREQUENCIA": item[1][4], "Similaridade": similarity}
            
            # Storing the for loops results in the list created before. 
            result1.append(data)

            # Transforming the list in a DataFrame. 
        df1 = pd.DataFrame(result1)
        
        

        # Subset the DataFrame where the similarity is over 80%
        df2 = df1[(df1['Similaridade'] >0.8) & (df1['Similaridade'] <= 1)].sort_values('Similaridade', ascending = False)
        df3 = df2[(df2[Coluna+"1"] != df2[Coluna+"2"])]
        
        Característica_indicada = []
        Frequencia = []
        for index, row in df3.iterrows():
            if row['NCM1_FREQUENCIA'] > row['NCM2_FREQUENCIA']:
                j = row['NCM1_indicado']
                _= row['NCM1_FREQUENCIA']
                Frequencia.append(_)
                Característica_indicada.append(j)
                               
            elif row['NCM2_FREQUENCIA'] > row['NCM1_FREQUENCIA']:
                j = row['NCM2_indicado']
                _= row['NCM2_FREQUENCIA']
                Frequencia.append(_)
                Característica_indicada.append(j)

            elif row['NCM1_indicado'].endswith(']'):
                j = 'Não tem indicação'
                _= 'Não tem indicação'
                Frequencia.append(_)
                Característica_indicada.append(j)

            elif row['NCM1_FREQUENCIA'] == row['NCM2_FREQUENCIA'] and row['NCM1_indicado'] == row['NCM2_indicado']:
                j = row['NCM1_indicado']
                _ = row['NCM1_FREQUENCIA']
                Característica_indicada.append(j)
                Frequencia.append(_)
            else: 
                j = 'Não tem indicação'
                _= 'Não tem indicação'
                Frequencia.append(_)
                Característica_indicada.append(j)

        df3[Coluna+'_indicada'] = Característica_indicada
        df3['Frequencia'] = Frequencia
        df3['Frequencia'] = df3['Frequencia'].apply(str)
        df4 = df3[['Material1', 'Descrição1', Coluna+"1", 'Material2', 'Descrição2', Coluna+"2", Coluna+'_indicada', 'Similaridade','Frequencia']]

        df5 = df4[['Material1', 'Descrição1', Coluna+"1", Coluna+'_indicada','Frequencia']]
        


        df5.rename( columns={'Material1':'Material', 'Descrição1':'Descrição', Coluna+'1': Coluna } ,inplace=True)
       
        
        df6 = df4[['Material2', 'Descrição2', Coluna+"2", Coluna+'_indicada', 'Frequencia']]
        df6.rename( columns={'Material2':'Material', 'Descrição2':'Descrição', Coluna+'2': Coluna } ,inplace=True)

        df7 = pd.concat([df5,df6],ignore_index = True)
        df7[Coluna] = df7[Coluna].apply(str)
        df7[Coluna+'_indicada'] = df7[Coluna+'_indicada'].apply(str)
        
        
        
        df8 = df7[df7[Coluna] != df7[Coluna+'_indicada']]

        df9 = df8.loc[df8.astype(str).drop_duplicates().index]
        df9 = df9.sort_values(Coluna+'_indicada', axis=0, ascending=True)
        df9 = df9.loc[df9.astype(str).drop_duplicates(subset = ['Material'], keep = 'last').index]
        

        df9['Descrição'] = df9['Descrição'].apply(str)
        y2['Descrição'] = y2['Descrição'].apply(str)
        df10 = pd.merge(df9, y2, how = 'inner', on = 'Descrição')
        df10.rename( columns={'Descrição': 'Descrição_','Material_x':'Material' } ,inplace=True)
        
        
        Acurácia = []
        
        for index, i in df10.iterrows():
            if i['Frequencia'] == 'Não tem indicação':
                x = 'Não tem indicação'
                Acurácia.append(x)
            else:
               x =  round(float(i['Frequencia']) / float(i['Material_y']) * 100)
               Acurácia.append(x)
        

        df10['Acurácia'] = Acurácia
        df10['Acurácia'] = df10['Acurácia'].apply(str)
        Q = []
        df11 = df10[['Material', 'Descrição_', Coluna, Coluna+'_indicada', 'Acurácia']]
        for i in df11['Descrição_']:
            f = i.split(",")

            Q.append(f)
        for i in Q:
            c = str(i).replace(',','')
            print(c)
                                 
        df11['Descrição'] = Q
        df12 = df11[['Material','Descrição',Coluna, Coluna+'_indicada', 'Acurácia']]
        df13 = pd.merge(df12, df, how = 'inner', on = 'Material')
        df14 = df13[['Material', 'Descrição_y', Coluna+'_x', Coluna+'_indicada', 'Acurácia']]
        df14.rename( columns={'Descrição_y': 'Descrição', Coluna+'_x':Coluna,'Acurácia': 'Acurácia %' } ,inplace=True)
        st.dataframe(df14)
                     
        df14.to_excel('Campos_diferentes.xlsx', index = False)
#else:
    #run3 = st.button("Instruções para o usuário")
    #if run3 == True:
        #d = {'Material':['123456'], 'Descrição':['Caneta azul'], 'Característica': ['0080']}
        #r = pd.DataFrame(d)
        #st.write('*Há dois tipos de análises, materiais duplicados e materiais duplicados com carecterísticas diferentes,  \n o arquivo anexo deve mudar de acodo com a opção escolhida.  \n Para materiais duplicados o arquivo deve estar com as seguintes colunas.*', r[['Material','Descrição']], '*Para materiais duplicados com características diferentes o arquivo deve estar com as seguintes colunas.*', r)
        #st.write('*Material = Código do item; Descrição = Descrição do item; Característica =  Parâmetro a ser analisado.  \n As Colunas precisam estar com os nomes exatamente iguais aos modelos.*')