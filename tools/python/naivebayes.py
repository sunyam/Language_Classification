import argparse
import csv

class CLI:
    def read(self):
        """Initialize a command line interface"""

        # Define arguments
        parser = argparse.ArgumentParser(description='Analyze csv file and apply naive bayes')
        parser.add_argument('-i','--input', nargs=1, help='CSV input file')
        parser.add_argument('-t','--test', nargs=1, help='Load test sentences from CSV file')
        parser.add_argument('-o','--out', nargs=1, help='Output test result to CSV file or -- for stdout')
        parser.add_argument('-f','--frequency', nargs=1, help='Show word frequency')
        parser.add_argument('-r','--ratio', nargs=1, 
                help='e.g. ê occurs 1000 in FR and 1 in SP, then if 1/1000 < r, remove it from SP')
        parser.add_argument('-s','--strict', action='store_true', 
                help='If a character is only available in one category then guess this category')
        args = parser.parse_args()

        # Create a naive bayes instance
        naiveBayes = NaiveBayes(args.strict)

        # Ratio
        ratio = 0

        # Checkfor missing arguments
        if args.input is None:
            print("Missing arguments")
            exit(1)

        # Update ratio
        if args.ratio is not None:
            ratio = float(args.ratio[0])

        # Log some information
        if ratio > 0:
            print(">> Ratio value:",ratio)
        if args.strict is True:
            print(">> Strict mode enabled")

        # Process input
        print(">> Loading:", args.input[0])
        with open(args.input[0], newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            naiveBayes.m_totalUtt = 0
            for row in reader:
                # Increment total utt
                naiveBayes.m_totalUtt += 1

                # Load attributes
                id = row['Id']
                category = row['Category']
                text = row['Text']

                # Tokenize text
                tokens = text.split()
                for token in tokens:

                    # Init first dimension
                    if token not in naiveBayes.m_wordGivenCategoryCounter:
                        naiveBayes.m_wordGivenCategoryCounter[token] = {}

                    # Init second dimension
                    if category not in naiveBayes.m_wordGivenCategoryCounter[token]:
                        naiveBayes.m_wordGivenCategoryCounter[token][category] = 0

                    # Increment counter
                    naiveBayes.m_wordGivenCategoryCounter[token][category] += 1


                # Init category counter
                if category not in naiveBayes.m_categoryCounter:
                    naiveBayes.m_categoryCounter[category] = 0

                # Increment category counter
                naiveBayes.m_categoryCounter[category] += 1

                # Init words per category counter
                if category not in naiveBayes.m_wordsInCategoryCounter:
                    naiveBayes.m_wordsInCategoryCounter[category] = 0

                # Increment words in category
                naiveBayes.m_wordsInCategoryCounter[category] += len(tokens)
            
            # Filter counters using the ratio value
            if ratio > 0:
                naiveBayes.applyRatio(ratio)

            # Compute probabilities
            naiveBayes.compute()

        # Print word frequency
        if args.frequency is not None and args.input is not None:
            # Show stats
            print(">> Printing word frequency of words occurring in {} category to stdout".format(args.frequency[0]))
            debug = []
            for w in naiveBayes.m_wordGivenCategoryCounter:
                if len(naiveBayes.m_wordGivenCategoryCounter[w]) == int(args.frequency[0]):
                    for c in naiveBayes.m_wordGivenCategoryCounter[w]:
                        debug.append({'word': w, 'count': naiveBayes.m_wordGivenCategoryCounter[w][c], 'category':c})
            debug.sort(key=lambda x: x['count'], reverse=True)
            for object in debug:
                print("Word {} orrcurs {} in {}".format(object['word'], object['count'], object['category']))

        # Prepare output
        output = "Id,Category\n"

        if args.test is not None:
            print(">> Evaluating test file:", args.test[0])
            with open(args.test[0], newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:

                    # Read csv attributes
                    id = row['Id']
                    text = row['Text']
                    
                    # Add output to csv
                    predict = naiveBayes.getCategory(text)
                    output += "{},{}\n".format(id, predict)

        # Process output
        if args.out is not None:
            if args.out[0] == "__":
                print(">> Printing output to stdout")
                print(output)
            else:
                print(">> Saving output to:",args.out[0])
                outputFile = open(args.out[0], 'w')
                outputFile.write(output)
                outputFile.close()

class NaiveBayes:
    def __init__(self, strict):
        """Initialize naive bayes variables"""
        
        # Set strict mode
        self.m_strict = strict

        # Total utterances
        self.m_totalUtt = 0

        # Count the number of utterances in each category
        self.m_categoryCounter= {}

        # Count the occurrence of a word in each category (e.g. var[word][cat])
        self.m_wordGivenCategoryCounter = {}

        # Count the number of words in each category
        self.m_wordsInCategoryCounter = {}

        # Store probability of a word given a category (e.g. var[word][cat])
        self.m_pWordGivenCategory = {}

        # Store the probility of a category
        self.m_pCategory = {}

    def getCategory(self, text):
        """Conclude category from the probabilities"""

        tokens = text.split()
        result = -1
        max = -1
        for category in self.m_pCategory:
            val = self.m_pCategory[category]
            for token in tokens:
                # If only one category, then return it
                if token in self.m_wordGivenCategoryCounter \
                        and self.m_strict is True \
                        and len(self.m_wordGivenCategoryCounter[token]) == 1:
                            return list(self.m_wordGivenCategoryCounter[token].keys())[0]
                # Otherwise, proceed with the production
                if token in self.m_pWordGivenCategory:
                    val *= self.m_pWordGivenCategory[token][category]
            # Argmax of production
            if val >= max:
                max = val
                result = category
        return result

    def applyRatio(self, ratio):
        """Apply ratio"""

        for token in self.m_wordGivenCategoryCounter:
            deleteCategories = set()
            # Check if category1/category2 < ratio, then mark it to delete
            for category1 in self.m_wordGivenCategoryCounter[token]:
                for category2 in self.m_wordGivenCategoryCounter[token]:
                    if category1 != category2 \
                            and self.m_wordGivenCategoryCounter[token][category1] / \
                            self.m_wordGivenCategoryCounter[token][category2] < ratio:
                                deleteCategories.add(category1)
            # Delete tokens in categories and update the number of words in category
            if len(deleteCategories) > 0:
                print(">>>> Word {} is currently in categories {}".format( 
                        token, self.m_wordGivenCategoryCounter[token]))
            for key in deleteCategories:
                print(">>>>>> Removing word {} from category {}"
                        .format(token, key, self.m_wordGivenCategoryCounter[token][key]))
                self.m_wordsInCategoryCounter[key] -= self.m_wordGivenCategoryCounter[token][key]
                self.m_wordGivenCategoryCounter[token].pop(key)

    def compute(self):
        """Compute probabilities"""

        BIAS = 0.00001
        print(">> Computing P(Wi|Cj)")
        for word in self.m_wordGivenCategoryCounter:

            # Init word probability
            if word not in self.m_pWordGivenCategory:
                self.m_pWordGivenCategory[word] = {}

            # Compute probabilities
            for category in self.m_categoryCounter:
                nominator = 0
                if category in self.m_wordGivenCategoryCounter[word]:
                    nominator = self.m_wordGivenCategoryCounter[word][category]
                self.m_pWordGivenCategory[word][category] = (BIAS + nominator) / \
                        (self.m_wordsInCategoryCounter[category] + len(self.m_wordGivenCategoryCounter))

        print(">> Computing P(Cj)")
        for category in self.m_categoryCounter:
            self.m_pCategory[category] = self.m_categoryCounter[category] / self.m_totalUtt

# Stat application
cli = CLI()
cli.read()
