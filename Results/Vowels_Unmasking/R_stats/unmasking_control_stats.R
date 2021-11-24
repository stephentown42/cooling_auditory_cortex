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


floz = read.csv( file.path( data_path, 'F1201.csv'))
virg = read.csv( file.path( data_path, 'F1203.csv'))
mini = read.csv( file.path( data_path, 'F1216.csv'))
clio = read.csv( file.path( data_path, 'F1217.csv'))
magnum = read.csv( file.path( data_path, 'F1311.csv'))
robin  = read.csv( file.path( data_path, 'F1509.csv'))


cols = c('fNum','treatment',"VowelLocation","SpatialCondition","Correct","Atten")

df = rbind(magnum[cols], robin[cols], floz[cols], virg[cols], mini[cols], clio[cols])
df <- subset(df, treatment=="False")

lose_mask <- subset(df, SpatialCondition!="separated")
srm <- subset(df, SpatialCondition!="single_speaker")


# Connect to text file for output
output_file = file.path('Results/Vowels_Unmasking', "unmasking_control_stats_report.txt")
sink(output_file)

print('Analysis run at:')
print(Sys.time())
print('########################################################')
print('########################################################')
print('########################################################')


# Look at spatial release from masking
control_mdl <- glmer(Correct ~ SpatialCondition*VowelLocation*Atten + (1|fNum), data=srm, family=binomial)

print('Control data: Colocated vs Separated')
print(summary(control_mdl))

print('########################################################')
print('########################################################')
print('########################################################')


# Sanity check - does removing noise entirely improve performance?
no_noise_mdl <- glmer(Correct ~ SpatialCondition*VowelLocation*Atten + (1|fNum), data=lose_mask, family=binomial)

print('Control data: Colocated vs Clean')
print(summary(no_noise_mdl))

print('########################################################')
print('########################################################')
print('########################################################')





