# Load the wordnet corpus
from nltk.corpus import wordnet
 
# Get a collection of synsets (synonym sets) for a word
synsets = wordnet.synsets( '' )
 
# Print the information
for synset in synsets:
  print "-" * 10
  print "Name:", synset.name
  print "Lexical Type:", synset.lexname
  print "Lemmas:", synset.lemma_names
  print "Definition:", synset.definition
  for example in synset.examples:
    print "Example:", example