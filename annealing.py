#READ ME:
    #A summary of this script is as follows. Overall this is a BQM approach to solving the tiling problem using a simulated D-wave QPU using DCC constraints.



from dimod import BinaryQuadraticModel
from neal import SimulatedAnnealingSampler
import pandas as pd



def export_to_excel(result_array, filename, filepath):
    # Create a DataFrame from the result_array
    df = pd.DataFrame(result_array, columns=["String", "Middle", "Frequency"])

    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(filepath + filename, engine="xlsxwriter")

    # Convert the DataFrame to an XlsxWriter Excel object without column headings
    df.to_excel(writer, sheet_name="Sheet1", index=False, header=False)

    # Close the Pandas Excel writer and output the Excel file
    writer.save()


#%%Create a blank Binary Quadratic Model (BQM)
bqm = BinaryQuadraticModel('BINARY')

for i in range(1, 13):
    xi = f"x{i}"
    bqm.add_variable(xi, 0)

gamma = 1  # Reward weight for being on the east wall
# Loop to add terms for the east wall constraint
for i in range(1, 13):
    xi = f"x{i}"

    # Add linear terms for the new objective
    if i <= 3 or 7 <= i <= 9:
        bqm.add_variable(xi, -gamma)
    else:
        bqm.add_variable(xi)
# %% think this bit is preventing them being in the same place
# Define penalty constant
penalty = 0

# Add ancilla variable
bqm.add_variable('z', -penalty * 6)  # Large negative bias to encourage z = 1

# Loop to add terms for each pair
for i in range(1, 7):
    x_sq1 = f"x{i}"
    x_sq2 = f"x{i + 6}"

    # Add XNOR constraint for this pair
    bqm.add_interaction(x_sq1, x_sq2, 2 * penalty)
    bqm.add_interaction(x_sq1, 'z', -2 * penalty)
    bqm.add_interaction(x_sq2, 'z', -2 * penalty)
    bqm.add_variable(x_sq1, penalty)
    bqm.add_variable(x_sq2, penalty)
    bqm.add_variable('z', penalty)


# %%
# Use the Simulated Annealing sampler
sampler = SimulatedAnnealingSampler()

# Sample the BQM
response = sampler.sample(bqm, num_reads=10000)
# %%
# Initialize an empty list to hold the samples
samples_list = []

# Iterate through the samples in the response
for sample, energy in response.data(['sample', 'energy']):
    # Convert the sample to a dictionary and add the energy
    sample_dict = dict(sample)
    sample_dict['energy'] = energy

    # Append this dictionary to the list
    samples_list.append(sample_dict)

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(samples_list)

df
# %%
df['Square 1'] = df[['x1', 'x2', 'x3', 'x4', 'x5', 'x6']].apply(lambda row: ''.join(row.map(str)), axis=1)
df['Square 2'] = df[['x7', 'x8', 'x9', 'x10', 'x11', 'x12']].apply(lambda row: ''.join(row.map(str)), axis=1)

df['Same Check'] = df.apply(lambda row: row['Square 1'] == row['Square 2'], axis=1)
# Group by the 'coord_1', 'coord_2', and 'energy' columns and count the frequency of each group
df_out = df.groupby(['Square 1', 'Square 2']).size().reset_index(name='frequency')

print('the number of times the tiles had the same position was:')
print(sum(df['Same Check']))


results = df_out.to_numpy()



#%%Exporting the results to an Excel sheet for plotting

    
    
filename = "BQM_simulated.xlsx" #choosing the file name
filepath = "/Users/kv18799/Library/CloudStorage/OneDrive-UniversityofBristol/Documents/PhD/Year 1/QC 4 Eng/DESIGN 24/Results/" #saving it in the design 24 file path

export_to_excel(results, filename, filepath) #running the function to export the results.
