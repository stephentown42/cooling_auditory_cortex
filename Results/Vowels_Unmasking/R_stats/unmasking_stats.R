# Analysis of effects of cortical inactivation on vowel discrimination in noise using logistic regression  

# Following the example given in:
# http://rstudio-pubs-static.s3.amazonaws.com/74431_8cbd662559f6451f9cd411545f28107f.html
#
#
# Version History:
#   Created: 2021-09-09 Stephen Town

# Clear all 
rm(list = ls())

# library(caret)        # for cross-validation
library(lme4)           # for mixed model
# library(stargazer)      # for reporting mixed models
library(scales)         # for rescaling signal level

# Load data and combine across subjects 
data_path = 'Results/Vowels_Unmasking/data/analysis'

magnum = read.csv( file.path( data_path, 'F1311.csv'))
robin  = read.csv( file.path( data_path, 'F1509.csv'))

df = rbind(magnum, robin)

lose_mask <- subset(df, SpatialCondition!="separated")
df <- subset(df, SpatialCondition!="single_speaker")


# Connect to text file for output
output_file = file.path('Results/Vowels_Unmasking', "unmasking_stats_report.txt")
sink(output_file)

print('Analysis run at:')
print(Sys.time())
print('########################################################')
print('########################################################')
print('########################################################')

# Run logistic regression
full_noSess <- glmer(Correct ~ treatment*SpatialCondition*VowelLocation + (1|fNum), data=df, family=binomial)

print('Bilateral cooling: Colocated vs Separated * Cooled vs. Control')
print(summary(full_noSess))

print('########################################################')
print('########################################################')
print('########################################################')

# Run logistic regression
full_noSess <- glmer(Correct ~ treatment*SpatialCondition*VowelLocation + (1|fNum), data=lose_mask, family=binomial)

print('Bilateral cooling: Colocated vs Single Speaker * Cooled vs. Control')
print(summary(full_noSess))

print('########################################################')
print('########################################################')
print('########################################################')

# Look at control data 
control_data <- subset(df, treatment == 'False')

control_mdl <- glmer(Correct ~ SpatialCondition*VowelLocation + (1|fNum), data=control_data, family=binomial)

print('Control data: Colocated vs Separated')
print(summary(control_mdl))

print('########################################################')
print('########################################################')
print('########################################################')

# Look at cooled data 
cooled_data <- subset(df, treatment == 'True')

cooled_mdl <- glmer(Correct ~ SpatialCondition*VowelLocation + (1|fNum), data=cooled_data, family=binomial)

print('Cooled data: Colocated vs Separated')
print(summary(cooled_mdl))


# Look at colocated data 
coloc_data <- subset(df, SpatialCondition == 'colocated')

coloc_mdl <- glmer(Correct ~ treatment + (1|fNum), data=coloc_data, family=binomial)

print('Colocated data: Control vs Cooled')
print(summary(coloc_mdl))

print('########################################################')
print('########################################################')
print('########################################################')

# Look at cooled data 
sep_data <- subset(df, SpatialCondition == 'separated')

sep_mdl <- glmer(Correct ~ treatment + (1|fNum), data=sep_data, family=binomial)

print('Separated data: Control vs Cooled')
print(summary(sep_mdl))

