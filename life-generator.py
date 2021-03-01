# Matthew Llanes
# Last Update: 2/28/2021

import csv
import sys
from tkinter import *
from tkinter import ttk
import os


def search_sort(search_results, top_amount):
    """
    Performs a series of sorts and slices to provide the top toys in given category
    :param search_results: list of products whose category matches user search
    :param top_amount: number of products to return
    :return: list of top_amount of top rated products from search results
    """
    search_results.sort(key=lambda item: item.uniq_id)  # sort by uniq_id
    search_results.sort(key=lambda item: item.num_of_reviews, reverse=True)  # then by number_of_reviews
    search_results = search_results[0:top_amount * 10]  # take top X*10
    search_results.sort(key=lambda item: item.uniq_id)  # re-sort by uniq_id
    search_results.sort(key=lambda item: item.avg_review_rating, reverse=True)  # then by average_review_rating
    search_results = search_results[0:top_amount]  # take top X
    return search_results


class CSVData:

    def __init__(self, infile):
        """Parse input file and create attributes from rows of dictionaries for easier access"""
        self.infile = infile  # csv file, in our case the kaggle amazon data
        self.main_product_list = []
        reader = csv.DictReader(open(infile, encoding='utf-8'))
        for row in reader:
            self.make_product(row)

    def make_product(self, row):
        """
        Creates Product object from DictReader dictionary and adds it to main product list
        :param row: one line from the csv file, one product with all info
        :return: None
        """
        uniq_id, product_name = row['uniq_id'], row['product_name']
        num_of_reviews, avg_review_rating = row['number_of_reviews'], row['average_review_rating']
        cat_and_sub_cat = row['amazon_category_and_sub_category']
        product = Product(uniq_id, product_name, num_of_reviews, avg_review_rating, cat_and_sub_cat)
        self.main_product_list.append(product)

    def user_search(self, category, top_amount):
        """
        Search CSVData for all items by input category to create new list of products
        :param category: user search category
        :param top_amount: how many toys to output
        :return: sorted list of top toys
        """
        search_results = []  # new list contains products whose main category matches search category
        for product in self.main_product_list:
            if product.main_category == category:
                search_results.append(product)
        return search_sort(search_results, top_amount)


class Product:
    """Represents a product from the kaggle dataset"""

    def __init__(self, uniq_id, product_name, num_of_reviews, avg_review_rating, cat_and_sub_cat):
        """
        Most attributes are retrieved directly from the CSV file,
        some are further extracted for pertinent meaning.
        """
        self.uniq_id = uniq_id
        self.product_name = product_name
        self.num_of_reviews = num_of_reviews
        self.avg_review_rating = avg_review_rating
        self.category_and_sub_category = cat_and_sub_cat
        self.main_category = self.get_main_category()

    def get_main_category(self):
        """
        Retrieves main category that the user will search for
        :return: string indicating the main category of a product
        """
        main_category = ''
        for letter in self.category_and_sub_category:
            if letter == ' ':
                break
            else:
                main_category += letter
        return main_category


def make_search_results_table(results):
    """
    :param results: products from user search
    :return: tuple containing lists of lists containing results data, and size of largest product name
    """
    out_table = [('item_name', 'item_rating', 'item_num_reviews')]
    size_of_longest_product_name = 0
    for product in results:
        out_table.append((product.product_name, product.avg_review_rating, product.num_of_reviews))
        if len(product.product_name) > size_of_longest_product_name:
            size_of_longest_product_name = len(product.product_name)
    return out_table, size_of_longest_product_name


class Window:

    def __init__(self, master, data):
        """Initializes GUI with its attributes"""
        self.main_window = master
        self.main_window.title('Life Generator')
        self.product_data = data
        prompt = 'Enter a category and number of top toys in that category to generate'
        self.prompt = ttk.Label(master, text=prompt, font=('Arial', 12)).pack()
        self.category_options = self.make_category_combobox()
        self.selected_number_to_generate = self.make_number_to_generate_spinbox()
        self.search_button = ttk.Button(master, text='See Results', command=self.process_search).pack()
        self.search_results = ttk.Frame(self.main_window)
        self.table_entry = ttk.Label(self.search_results)

    def get_categories(self):
        """:return: list of categories from kaggle dataset"""
        categories = []
        for product in self.product_data.main_product_list:
            if product.main_category not in categories and product.main_category != '':
                categories.append(product.main_category)
            else:
                continue
        return categories

    def make_category_combobox(self):
        """:return: combobox full of categories from kaggle data for user to choose from"""
        combobox = ttk.Combobox(self.main_window)
        categories = self.get_categories()
        combobox['values'] = categories
        combobox.set(categories[0])
        combobox.pack()
        return combobox

    def make_number_to_generate_spinbox(self):
        """:return: spinbox for reference by window object"""
        number_to_generate_spinbox = ttk.Spinbox(self.main_window, from_=1, to=10000, increment=10)
        number_to_generate_spinbox.set('1')
        number_to_generate_spinbox.pack()
        return number_to_generate_spinbox

    def perform_search(self):
        """:return: results from user user search"""
        category = self.category_options.get()
        top_amount = self.selected_number_to_generate.get()
        results = self.product_data.user_search(category, int(top_amount))
        input_data = ['toys', category, top_amount]
        return input_data, results

    def display_results_in_gui(self, out_table):
        """
        :param out_table: tuple containing lists of lists containing results data, and size of largest product name
        :return: None
        """
        for i in range(len(out_table[0])):
            for j in range(3):
                if j == 0:
                    width = out_table[1]
                else:
                    width = 20
                self.table_entry = ttk.Label(self.search_results, width=width)
                self.table_entry.grid(row=i, column=j)
                self.table_entry.config(text=out_table[0][i][j])

    def process_search(self):
        """
        Function to process search and output data to outfile and/or GUI table
        :return: None
        """
        self.search_results.destroy()
        self.search_results = ttk.Frame(self.main_window)
        results = self.perform_search()
        make_outfile(results[0], results[1])
        out_table = make_search_results_table(results[1])
        self.display_results_in_gui(out_table)
        self.search_results.pack()


class ContentGenerator:
    """Microservice provided by other student, will use output file to display information to the user"""

    def __init__(self):
        self.path = "C:\\Users\\Idabeard\\SoftwareEngineering1\\Daniel D's Content Generator\\output.csv"
        self.wiki_paragraph = None
        self.primary_keyword = None
        self.secondary_keyword = None
        self.process_content_generated()

    def does_path_exist(self):
        """

        :return:
        """
        return os.path.exists(self.path)

    def process_content_generated(self):
        """

        :return:
        """
        if os.path.exists(self.path):
            reader = csv.reader(open(self.path))
            next(reader)
            next(reader)
            content = next(reader)
            self.make_keywords(content[0])
            self.wiki_paragraph = content[1]

    def make_keywords(self, keywords):
        """
        :param keywords: string with a primary and secondary keyword, separated by a ;
        :return: None
        """
        primary = ''
        i = 0
        while keywords[i] != ';':
            primary += keywords[i]
            i += 1
        self.primary_keyword, self.secondary_keyword = primary, keywords[i + 1:]


def process_infile(filename):
    """
    :param filename: input file from command line
    :return: search criteria from input file
    """
    reader = csv.reader(open(filename))
    line_data = next(reader)
    return line_data


def make_outfile(search_criteria, output):
    """
    Formats and outputs csv file from results obtained from user search
    :param search_criteria: search criteria
    :param output: list of product objects(toys)
    :return: None, writes outfile
    """
    with open('output.csv', 'w') as outfile:
        first_head_half = 'input_item_type,input_item_category,input_number_to_generate,output_item_name,'
        second_head_half = 'output_item_rating,output_item_num_reviews'
        outfile.write(first_head_half + second_head_half + '\n')
        for product in output:
            criteria_str = search_criteria[0] + ',' + search_criteria[1] + ',' + search_criteria[2] + ','
            product_info = product.product_name + ',' + product.avg_review_rating + ',' + product.num_of_reviews
            outfile.write(criteria_str + product_info + '\n')


def main():
    """
    Driver code to start program. Decision based on whether program
    is started with input file on command line or used with GUI
    :return: None
    """
    content = ContentGenerator()
    kaggle_data = CSVData('amazon_co-ecommerce_sample.csv')
    if len(sys.argv) == 2:  # if there's an input file, make an output file w/o GUI
        infile_data = process_infile(sys.argv[1])
        results = kaggle_data.user_search(infile_data[1], int(infile_data[2]))
        make_outfile(infile_data, results)
    else:  # otherwise, start GUI
        root = Tk()
        app = Window(root, kaggle_data)
        root.mainloop()


if __name__ == '__main__':
    main()
