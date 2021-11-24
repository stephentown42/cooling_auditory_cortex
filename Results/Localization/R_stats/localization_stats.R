# Analysis of effects of cortical inactivation on sound localization using logistic / poisson regression  
#
# 
# Notes:
# Modelling response error with gamma distributions won't work as they can't handle zeros
# 
# 
# Version History:
#   Created: 2021-09-11 Stephen Town


# Combine data across ferrets and run a generalized linear mixed model to
# determine the effect of cooling on absolute error, with subject and test 
# session as random effects, and cooling as fixed effects


# Clear all 
rm(list = ls())

# Load libraries
library(lme4)           # for mixed model

# Load data
data_path = 'Results/Localization/data/analysis'

magnum = read.csv( file.path( data_path, 'F1311.csv'))
robin  = read.csv( file.path( data_path, 'F1509.csv'))

# Add label to identify subjects
magnum$fNum <- 1311
robin$fNum  <- 1509

# Combine data across subjects
df = rbind(magnum, robin)

# Connect to text file for output
output_file = file.path('Results/Localization', "localization_stats_report.txt")
sink(output_file)

print('Analysis run at:')
print(Sys.time())


###################################################################################
# Analysis 1: Bilateral Cooling vs. Control
print('########################################################')
print('########################################################')
print('Bilateral vs. Control')

# Filter data
bc = df[df$Condition %in% c("Bilateral","Control"),]

# Logistic regression on probability of localizing
correct_mix = glmer(Correct ~ 1 + Condition + (1|fNum), family=binomial, data=bc)
print( summary(correct_mix))


print('########################################################')
print('########################################################')


# Logistic regression on probability of responding correctly
error_mix = glmer(Error ~ 1 + Condition + (1|fNum), family=poisson, data=bc)
print(summary(error_mix))



########################################################
# Analysis 2: Unilateral Cooling
print('########################################################')
print('########################################################')
print('########################################################')

print('Unilateral cooling: Left vs. Right')

lr = df[df$Condition %in% c("Left","Right"),]

# Logistic regression on probability of responding correctly
correct_mix_LR = glmer(Correct ~ 1 + Condition*Spkr_Rad + (1|fNum), family=binomial, data=lr)
print(summary(correct_mix_LR))

print('########################################################')
print('########################################################')

# Logistic regression on probability of responding correctly
error_mix_LR = glmer(Error ~ 1 + Condition*Spkr_Rad + (1|fNum), family=poisson, data=lr)
print(summary(error_mix_LR))



########################################################
# Return control to console
sink()  