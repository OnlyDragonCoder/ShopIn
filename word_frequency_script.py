
# coding: utf-8

# In[3]:


from wordhelper_funcs import *

class word_frequency(object):    
    
    def __init__(self):
#         args = get_arguments()
        self.file_path = '/home/himanshu/Downloads/CSVs for TF'
#         self.file_name = './NM_Lingerie_Sleepwear_Swimwear.xls'
        self.master_list_path = './Master_List_1308.csv'
        self.xls_sheet_name = 'Swimwear&Coverups'
        os.chdir(self.file_path)

#     def get_arguments():
#         parser = argparse.ArgumentParser(description="Word-frequency Calculator")
#         parser.add_argument("--file_path", type=str,
#                             help="Path of the directory containing the data file.")
#         parser.add_argument("--file_name", type=str,
#                             help="Name of the data file with extension(eg:fname.csv).")
#         parser.add_argument("--master_list_path", type=str,
#                            help="Name of the Master list file(with extension) if in the same directory as data(otherwise complete path)")

    def read_file(self):
#         if self.file_name.endswith('.csv'):
        data = pd.DataFrame()
        dirs = ['./LA Senza/Sport/*.csv']
        for j in dirs:    
            for i in glob.glob(j):
                y = pd.read_csv(i, usecols=['category','prodName','imageName','description'])
                data = data.append(y, ignore_index=True)
#         elif self.file_name.endswith('.xls'):
#             data = pd.read_excel(self.file_name, sheet_name = self.xls_sheet_name,nrows=5)
        return data

    def count_cat(self,dataframe, path, ret_nb):
        def xx(x):
            if x.endswith('-'):
                return x[:-1]
            return x
        master_listx = read_master_list(path)
#         master_listx = master_listx[0:50]
        df_word_list = []
        master_list_i = []
        # Remove this loop
        for i,j in dataframe.category.apply(lambda x: get_word_frequency_from_cat(x, master_listx, remove_similar = False)):
            df_word_list.extend(i)
            master_list_i.extend(j)
        try:
            category_count = pd.DataFrame(pd.DataFrame(df_word_list)[0].value_counts()).reset_index()
        except KeyError as e:
            print('No new term found!')
            return
        category_count.columns = ['category',ret_nb]
        category_count.category = category_count.category.apply(lambda x: xx(x))
        return category_count, pd.DataFrame(sorted(set(master_list_i)))
    
    def count_pn(self, dataframe, path, ret_nb):
        def xx(x):
            if x.endswith('-'):
                return x[:-1]
            return x        
        master_listx = read_master_list(path)
#         master_listx = master_listx[0:50]
        df_word_list = []
        master_list_i= []
        # Remove this loop
        for i,j in dataframe.prodName.apply(lambda x: get_word_frequency_from_pn(x, master_listx, remove_similar = False)):
            df_word_list.extend(i)
            master_list_i.extend(j)
        try:
            prodName_count = pd.DataFrame(pd.DataFrame(df_word_list)[0].value_counts()).reset_index()
        except KeyError as e:
            print('No new term found!')
            return
        prodName_count.columns = ['prodName',ret_nb]
        prodName_count.prodName = prodName_count.prodName.apply(lambda x: xx(x))
        return prodName_count, pd.DataFrame(sorted(set(master_list_i)))
    
    def count_pd(self, dataframe, path, ret_nb):
        def xx(x):
            if x.endswith('-'):
                return x[:-1]
            return x        
        master_listx = read_master_list(path)
#         master_listx = master_listx[0:50]
        df_word_list = []
        master_list_i= []
        # Remove this loop
        for i,j in dataframe.description.apply(lambda x: get_word_frequency_from_pd(x, master_listx,remove_similar = False)):
            df_word_list.extend(i)
            master_list_i.extend(j)
        try:
            prodDesc_count = pd.DataFrame(pd.DataFrame(df_word_list)[0].value_counts()).reset_index()
        except KeyError as e:
            print('No new term found!')
            return
        prodDesc_count.columns = ['prodDesc',ret_nb]
        prodDesc_count.prodDesc = prodDesc_count.prodDesc.apply(lambda x: xx(x))
        return prodDesc_count, pd.DataFrame(sorted(set(master_list_i)))
    
    def prep_data(self, data, category=False, prodName=False, prodDesc=False):
        master_list = []
        category_pivot = pd.DataFrame()
        prodName_pivot = pd.DataFrame()
        prodDesc_pivot = pd.DataFrame()
        data['retailer_key'] = data.imageName.str.split('_',expand=True)[0]
        "if category equals to True outputs category frequency count"
        if category:
            cat_data = data[['category','retailer_key']]
            retailers = pd.DataFrame(cat_data.retailer_key.unique(), columns =['retailer_key'])
            retailers['index'] = retailers.index.get_values()
            print('Unique retailers with index values..\n')
            print(retailers.values)
            for rname, i in retailers.values:
                r_sub = cat_data[cat_data.retailer_key == rname]
                R_cat_i, master_list_i = self.count_cat(r_sub, path = self.master_list_path, ret_nb=rname)
                master_list.append(master_list_i)
                if i==0:
                    category_pivot = R_cat_i
                elif i>0:
                    category_pivot = category_pivot.merge(R_cat_i, on = 'category', how = 'outer')
            category_pivot = category_pivot.fillna(0)
            
        "if prodName equals to True outputs prodName frequency count"            
        if prodName:
            pn_data = data[['prodName','retailer_key']]
            retailers = pd.DataFrame(pn_data.retailer_key.unique(), columns =['retailer_key'])
            retailers['index'] = retailers.index.get_values()
            for rname, i in retailers.values:
                r_sub = pn_data[pn_data.retailer_key == rname]
                R_pn_i, master_list_i = self.count_pn(r_sub, path=self.master_list_path, ret_nb=rname)
                master_list.append(master_list_i)
                if i<1:
                    prodName_pivot = R_pn_i
                else:
                    prodName_pivot = prodName_pivot.merge(R_pn_i, on = 'prodName', how = 'outer')
            prodName_pivot = prodName_pivot.fillna(0)
        
        "if prodDesc equals to True outputs description frequency count"            
        if prodDesc:
            pd_data = data[['description','retailer_key']]
            retailers = pd.DataFrame(pd_data.retailer_key.unique(), columns =['retailer_key'])
            retailers['index'] = retailers.index.get_values()
            for rname, i in retailers.values:
                r_sub = pd_data[pd_data.retailer_key == rname]
                R_pd_i, master_list_i = self.count_pd(r_sub, path=self.master_list_path, ret_nb=rname)
                master_list.append(master_list_i)
                if i<1:
                    prodDesc_pivot = R_pd_i
                else:
                    prodDesc_pivot = prodDesc_pivot.merge(R_pd_i, on = 'prodDesc', how = 'outer')
            prodDesc_pivot = prodDesc_pivot.fillna(0)
        return category_pivot, prodName_pivot, prodDesc_pivot, master_list
    
if __name__ == "__main__":
    main = word_frequency()
    data = main.read_file()
    category_pivot, prodName_pivot, prodDesc_pivot, master_list = main.prep_data(data, category = True, prodName = True, prodDesc = True)


# In[5]:


prodDesc_pivot.to_csv('LS_sport_prodDesc_pivot.csv',index=False,header=True)
prodName_pivot.to_csv('LS_sport_prodName_pivot.csv',index=False,header=True)
category_pivot.to_csv('LS_sport_category_pivot.csv',index=False,header=True)


# In[6]:


category_pivot

