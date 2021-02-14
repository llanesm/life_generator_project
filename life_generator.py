# Matthew Llanes
# 2/12/2021

import csv
import sys
from tkinter import *
from tkinter import ttk


class CSVData:
    """Data from csv file"""

    def __init__(self, infile):
        """
        Parse input file and create attributes from rows of dictionaries for easier access
        """
        self.infile = infile  # csv file, in our case the kaggle amazon data
        self.main_product_list = []  # list of Toy objects
        reader = csv.DictReader(open(infile, encoding='utf-8'))  # to make parsing data easier
        for row in reader:
            self.main_product_list.append(Product(row['uniq_id'], row['product_name'], row['manufacturer'],
                                                  row['price'], row['number_available_in_stock'],
                                                  row['number_of_reviews'], row['number_of_answered_questions'],
                                                  row['average_review_rating'], row['amazon_category_and_sub_category'],
                                                  row['customers_who_bought_this_item_also_bought'], row['description'],
                                                  row['product_information'], row['product_description'],
                                                  row['items_customers_buy_after_viewing_this_item'],
                                                  row['customer_questions_and_answers'], row['customer_reviews'],
                                                  row['sellers']))

    def user_search(self, category, top_amount):
        """
        Search CSVData for all items by input category to create new list of products, then performs
        a series of sorts and slices to provide the top toys in given category
        :param category: user search category
        :param top_amount: how many toys to output
        :return: sorted list of top toys
        """
        # new list contains products whose main category matches search category
        search_results = []
        for product in self.main_product_list:
            if product.main_category == category:
                search_results.append(product)
            else:
                continue

        # series of sorts to meet requirements
        search_results.sort(key=lambda item: item.uniq_id)  # sort by uniq_id
        search_results.sort(key=lambda item: item.number_of_reviews, reverse=True)    # then by number_of_reviews
        search_results = search_results[0:top_amount * 10]   # take top X*10
        search_results.sort(key=lambda item: item.uniq_id)  # resort by uniq_id
        search_results.sort(key=lambda item: item.average_review_rating, reverse=True)  # then by average_review_rating
        search_results = search_results[0:top_amount]   # take top X
        return search_results


class Product:
    """Represents a product from the kaggle dataset"""

    def __init__(self, uniq_id, product_name, manufacturer, price, number_available_in_stock, number_of_reviews,
                 number_of_answered_questions, average_review_rating, amazon_category_and_sub_category,
                 customers_who_bought_this_item_also_bought, description, product_information, product_description,
                 items_customers_buy_after_viewing_this_item, customer_questions_and_answers,
                 customer_reviews, sellers):
        """
        Initializes attributes for a product object. Most are retrieve directly from the
        CSV file, some are further extracted for pertinent meaning.
        """
        self.uniq_id = uniq_id
        self.product_name = product_name
        self.manufacturer = manufacturer
        self.price = price
        self.number_available_in_stock = number_available_in_stock
        self.number_of_reviews = number_of_reviews
        self.number_of_answered_questions = number_of_answered_questions
        self.average_review_rating = average_review_rating
        self.amazon_category_and_sub_category = amazon_category_and_sub_category
        self.customers_who_bought_this_item_also_bought = customers_who_bought_this_item_also_bought
        self.description = description
        self.product_information = product_information
        self.product_description = product_description
        self.items_customers_buy_after_viewing_this_item = items_customers_buy_after_viewing_this_item
        self.customer_questions_and_answers = customer_questions_and_answers
        self.customer_reviews = customer_reviews
        self.sellers = sellers

        self.main_category = self.get_main_category()  # category a user will search for

    def get_main_category(self):
        """
        Adds letters to a string until a space is found
        :return: string indicating the main category of a product
        """
        main_category = ''

        for letter in self.amazon_category_and_sub_category:
            if letter == ' ':
                break
            else:
                main_category += letter

        return main_category


class Window:

    def __init__(self, master, data):
        """Initializes GUI"""
        # main window
        self.master = master
        master.title('Life Generator')

        self.prompt = ttk.Label(master, text='Enter a category and number of top toys in that category to generate')
        self.prompt.pack()

        # list of toys from kaggle
        self.data = data

        # category options for user to choose from
        self.enter_category = ttk.Combobox(master)
        categories = self.get_categories()
        self.enter_category['values'] = categories
        self.enter_category.set(categories[0])
        self.enter_category.pack()

        # user selects number of products to generate
        self.number_to_generate = ttk.Spinbox(master, from_=1, to=10000, increment=10)
        self.number_to_generate.set('0')    # sets initial value to 1
        self.number_to_generate.pack()

        # button to initiate search and output
        self.search = ttk.Button(master, text='See Results', command=self.process_search)
        self.search.pack()

        self.search_results = ttk.Label(master)
        self.search_results.pack()

    def get_categories(self):
        """
        Retrieves all categories from kaggle dataset and adds them to listbox in GUI
        :return: None, adds entries to categories listbox
        """
        categories = []
        for product in self.data.main_product_list:
            if product.main_category not in categories and product.main_category != '':
                categories.append(product.main_category)
            else:
                continue
        return categories

    def process_search(self):
        """
        Function to process search and output data to appropriate places
        :param category: selected category from enter_category Combobox
        :param top_amount: selected amount from number_to_generate scrollbox
        :return:
        """
        category = self.enter_category.get()    # user's entered category
        top_amount = self.number_to_generate.get()  # user's entered number they want to generate
        results = self.data.user_search(category, int(top_amount))  # runs code for the search
        input_data = ['toys', category, top_amount]     # for output file
        make_outfile(input_data, results)   # per requirements

        # display search results in GUI
        display_label = 'item_name,item_rating,item_num_reviews\n'
        for product in results:
            display_label += product.product_name + ',' + product.average_review_rating + ',' + \
                             product.number_of_reviews + '\n'
        self.search_results.config(text=display_label)  # update label with results


def process_infile(filename):
    """
    Processes command line file argument
    :param filename: input file from command line
    :return:
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
        outfile.write('input_item_type,input_item_category,input_number_to_generate,output_item_name,'
                      'output_item_rating,output_item_num_reviews\n')   # header row
        # write row for each product in output
        for product in output:
            outfile.write(search_criteria[0] + ',' + search_criteria[1] + ',' + search_criteria[2] + ',' +
                          product.product_name + ',' + product.average_review_rating + ',' + product.number_of_reviews
                          + '\n')


def main():
    """

    :return: None
    """
    # make object from csv data
    kaggle_data = CSVData('amazon_co-ecommerce_sample.csv')

    # if there's an input file, just make an output file
    if len(sys.argv) == 3:
        infile_data = process_infile(sys.argv[1])
        results = kaggle_data.user_search(infile_data[1], int(infile_data[2]))
        make_outfile(infile_data, results)
    # otherwise, start GUI
    else:
        root = Tk()
        app = Window(root, kaggle_data)
        root.mainloop()


if __name__ == '__main__':
    main()
