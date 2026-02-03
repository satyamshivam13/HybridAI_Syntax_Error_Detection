"""
Targeted augmentation for low-precision/recall error types.
Addresses: DivisionByZero, InvalidAssignment, MissingDelimiter, TypeMismatch
"""

import pandas as pd
import random
import numpy as np

# Set random seeds for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Load existing dataset
df = pd.read_csv('dataset/merged/all_errors.csv')

print(f"Current dataset size: {len(df)}")
print("\nCurrent distribution of weak error types:")
weak_errors = ['DivisionByZero', 'InvalidAssignment', 'MissingDelimiter', 'TypeMismatch']
for error in weak_errors:
    count = len(df[df['error_type'] == error])
    print(f"  {error}: {count}")

# ============================================================
# DivisionByZero - Need more diverse patterns
# ============================================================
division_by_zero_samples = []

# Python patterns
for i in range(40):
    patterns = [
        f"result = {random.randint(1, 100)} / 0\nprint(result)",
        f"x = 0\ny = {random.randint(1, 100)} / x",
        f"def calculate():\n    denominator = 0\n    return {random.randint(1, 100)} / denominator",
        f"numbers = [{', '.join(str(random.randint(0, 10)) for _ in range(5))}]\nresult = {random.randint(1, 100)} / numbers[{random.randint(0, 4)}]",
    ]
    division_by_zero_samples.append({
        'buggy_code': random.choice(patterns),
        'error_type': 'DivisionByZero',
        'language': 'Python'
    })

# ...existing code for other error types and sample generation...

# Combine all new samples
type_mismatch_samples = []  # Placeholder for other error types
new_samples = (
    division_by_zero_samples +
    type_mismatch_samples
)

print(f"\n{'='*60}")
print(f"Total new samples generated: {len(new_samples)}")
print(f"{'='*60}")

# Create DataFrame with new samples
new_df = pd.DataFrame(new_samples)

# Deduplication: Remove samples that already exist in the dataset
print("\n🔍 Checking for duplicates...")
existing_codes = set(df['buggy_code'].values)
initial_new_count = len(new_df)
new_df = new_df[~new_df['buggy_code'].isin(existing_codes)]
duplicates_removed = initial_new_count - len(new_df)

if duplicates_removed > 0:
    print(f"⚠️  Removed {duplicates_removed} duplicate samples")
print(f"✅ After deduplication: {len(new_df)} truly new samples")

# Append to existing dataset
augmented_df = pd.concat([df, new_df], ignore_index=True)

# Save augmented dataset
augmented_df.to_csv('dataset/merged/all_errors.csv', index=False)

print(f"\n✅ Augmented dataset saved!")
print(f"Previous size: {len(df)}")
print(f"New size: {len(augmented_df)}")
print(f"Samples added: {len(new_df)}")

print("\n📊 Updated distribution:")
# ...existing code for updated distribution...
