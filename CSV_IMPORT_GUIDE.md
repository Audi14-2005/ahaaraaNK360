# 🍎 CSV Import Guide for AAHAARA 360

## 📋 How to Import Your Own CSV Files

### Step 1: Prepare Your CSV File

Your CSV file must have these **exact column names** (case-sensitive):

#### Required Columns:
- `Food Item` - Name of the food
- `Meal Type` - Breakfast, Lunch, Dinner, Snack
- `Calories (k)` - Calories per 100g
- `Carbs (g)` - Carbohydrates per 100g
- `Protein (g)` - Protein per 100g
- `Fat (g)` - Fat per 100g
- `Fibre (g)` - Fiber per 100g

#### Optional Columns:
- `Category` - Food category
- `Tags` - Food tags
- `Rasa` - Taste (Sweet, Sour, Salty, Pungent, Bitter, Astringent)
- `Virya` - Energy (Heating, Cooling, Neutral)
- `Vipaka` - Post-digestive effect (Sweet, Sour, Pungent)
- `Guna` - Qualities (Light, Heavy, Dry, Oily, Cold, Hot)
- `Dosha Effect` - Effect on doshas (Pacifies, Aggravates, Neutral)

### Step 2: Download Template (Optional)

1. Go to: http://127.0.0.1:8000/food-scanner/database/
2. Click "Import Foods CSV"
3. Click "Download CSV Template" to get the exact format

### Step 3: Import Your CSV

1. Go to: http://127.0.0.1:8000/food-scanner/database/
2. Click "Import Foods CSV"
3. Upload your CSV file
4. Click "Import Foods"

### Step 4: Verify Import

After import, you'll see:
- ✅ Success message with count of imported foods
- ✅ Automatic sync to diet planner database
- ✅ Foods available in both Food Scanner and Diet Planner

## 🎯 Using Your Imported Foods

### Food Scanner
- Go to: http://127.0.0.1:8000/food-scanner/scan/
- Upload any food image
- System will show nutritional data from your imported foods

### Diet Planner
- Go to: http://127.0.0.1:8000/diet-planner/patients/create/
- Create a patient
- Generate diet chart
- System will use your imported foods in meal plans

## 📊 Example CSV Format

```csv
Food Item,Meal Type,Calories (k),Carbs (g),Protein (g),Fat (g),Fibre (g),Category,Tags,Rasa,Virya,Vipaka,Guna,Dosha Effect
Rice,Lunch,130,28,2.7,0.3,0.4,Grains,staple,Sweet,Neutral,Sweet,Light,Neutral
Chicken,Dinner,165,0,31,3.6,0,Protein,lean,Sweet,Heating,Sweet,Light,Pacifies
Apple,Snack,52,14,0.3,0.2,2.4,Fruits,fresh,Sweet,Heating,Sweet,Light,Pacifies
```

## 🔧 Troubleshooting

### Common Issues:
1. **Column names don't match** - Use exact names from template
2. **Empty values** - Use 0 for missing nutritional data
3. **Invalid choices** - Use only the specified values for Rasa, Virya, etc.

### Success Indicators:
- ✅ Green success message after import
- ✅ Foods appear in database table
- ✅ Foods available in diet chart generation
- ✅ Foods show up in food scanner results

## 🚀 Advanced Features

### Automatic Sync
- When you import CSV, data automatically syncs to both databases
- No manual sync needed
- Foods immediately available in diet planner

### Smart Matching
- Food scanner tries to match uploaded images with your database
- Falls back to demo data if no match found
- Uses real nutritional data when match is found

### Diet Chart Integration
- All imported foods are available for diet chart generation
- System considers nutritional values and Ayurvedic properties
- Generates personalized meal plans based on your data

## 📞 Support

If you encounter any issues:
1. Check the CSV format matches the template exactly
2. Ensure all required columns are present
3. Verify data types (numbers for nutritional values)
4. Check the server logs for detailed error messages

---

**Happy Importing! 🎉**

