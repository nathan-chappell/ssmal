# ones_then_twos
# read 1* 2*

# happy path
reading_ones 1 reading_ones 0 R
reading_ones 2 reading_twos 0 R
reading_twos 2 reading_twos 0 R

# failures
reading_ones 0 FAIL 0 R
reading_twos 0 SUCCESS 0 R
reading_twos 1 FAIL 0 R
