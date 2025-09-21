# 🍎 CSV Food Import Guide - Diet Planner

## 📋 **Overview**

The Diet Planner now supports importing foods from CSV files, making it easy to populate your food database with comprehensive nutritional and Ayurvedic data.

## 📁 **CSV File Format**

Your CSV file must include the following columns (in any order):

### **Required Columns:**
- `name` - Food name (e.g., "Basmati Rice")
- `category` - Food category (e.g., "grains", "vegetables", "fruits", "proteins", "dairy", "spices")
- `calories` - Calories per 100g (integer)
- `protein` - Protein per 100g (decimal)
- `carbohydrates` - Carbohydrates per 100g (decimal)
- `fat` - Fat per 100g (decimal)
- `fiber` - Fiber per 100g (decimal)
- `primary_taste` - Primary taste (sweet, sour, salty, pungent, bitter, astringent)
- `energy` - Energy property (cooling, heating, neutral)
- `vata_effect` - Effect on Vata (pacifies, aggravates, neutral)
- `pitta_effect` - Effect on Pitta (pacifies, aggravates, neutral)
- `kapha_effect` - Effect on Kapha (pacifies, aggravates, neutral)

### **Optional Columns:**
- `subcategory` - Food subcategory (e.g., "white_rice", "leafy_greens")
- `secondary_taste` - Secondary taste (leave empty if none)
- `is_vegetarian` - Boolean (true/false, default: true)
- `is_vegan` - Boolean (true/false, default: true)
- `is_gluten_free` - Boolean (true/false, default: true)
- `is_dairy_free` - Boolean (true/false, default: true)
- `contains_nuts` - Boolean (true/false, default: false)
- `contains_soy` - Boolean (true/false, default: false)
- `contains_eggs` - Boolean (true/false, default: false)
- `contains_fish` - Boolean (true/false, default: false)
- `contains_shellfish` - Boolean (true/false, default: false)

## 📝 **Sample CSV Structure**

```csv
name,category,subcategory,calories,protein,carbohydrates,fat,fiber,primary_taste,secondary_taste,energy,vata_effect,pitta_effect,kapha_effect,is_vegetarian,is_vegan,is_gluten_free,is_dairy_free,contains_nuts,contains_soy,contains_eggs,contains_fish,contains_shellfish
Basmati Rice,grains,white_rice,130,2.7,28.0,0.3,0.4,sweet,,cooling,pacifies,pacifies,aggravates,True,True,True,True,False,False,False,False,False
Spinach,vegetables,leafy_greens,23,2.9,3.6,0.4,2.2,bitter,astringent,cooling,aggravates,pacifies,pacifies,True,True,True,True,False,False,False,False,False
```

## 🚀 **How to Import Foods**

### **Method 1: Using Django Management Command**

1. **Prepare your CSV file** with the required format
2. **Run the import command:**
   ```bash
   python manage.py import_foods_csv your_foods.csv
   ```
3. **To clear existing foods and import fresh:**
   ```bash
   python manage.py import_foods_csv your_foods.csv --clear
   ```

### **Method 2: Using the Sample File**

1. **Use the provided sample file:**
   ```bash
   python manage.py import_foods_csv sample_foods.csv --clear
   ```
2. **This will import 17 sample foods** with complete Ayurvedic properties

## 📊 **Import Results**

The command will show you:
- ✅ **Successfully imported foods**
- ⚠️ **Foods that already exist** (skipped)
- ❌ **Errors encountered** (with row numbers)
- 📊 **Total foods in database**

## 🎯 **Ayurvedic Properties Guide**

### **Taste (Rasa):**
- `sweet` - Madhura (nourishing, grounding)
- `sour` - Amla (stimulating, heating)
- `salty` - Lavana (moistening, heating)
- `pungent` - Katu (stimulating, heating)
- `bitter` - Tikta (cooling, detoxifying)
- `astringent` - Kashaya (cooling, drying)

### **Energy (Virya):**
- `cooling` - Sheeta (reduces Pitta, increases Vata/Kapha)
- `heating` - Ushna (reduces Vata/Kapha, increases Pitta)
- `neutral` - Madhya (balanced effect)

### **Dosha Effects:**
- `pacifies` - Reduces the dosha
- `aggravates` - Increases the dosha
- `neutral` - No significant effect

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"NOT NULL constraint failed"**
   - Make sure all required columns are present
   - Check that numeric values are valid numbers

2. **"Invalid taste/energy/dosha effect"**
   - Use only the exact values listed in the guide
   - Check spelling and case sensitivity

3. **"File not found"**
   - Make sure the CSV file path is correct
   - Use absolute path if needed

### **Data Validation:**

- **Numeric fields** must be valid numbers
- **Boolean fields** accept: true/false, 1/0, yes/no, on/off
- **Choice fields** must match exact values from the guide
- **Empty secondary_taste** is allowed (leave blank)

## 📈 **Best Practices**

### **For Large Datasets:**
1. **Test with small batches** first
2. **Use the --clear flag** only when necessary
3. **Backup your database** before major imports
4. **Validate data** before importing

### **For Ayurvedic Accuracy:**
1. **Research authentic sources** for Ayurvedic properties
2. **Consult Ayurvedic texts** for accurate taste and energy classifications
3. **Verify dosha effects** with qualified practitioners
4. **Use consistent terminology** across your dataset

## 🎉 **After Import**

Once your foods are imported:

1. **Visit the Food Database** at `/diet-planner/foods/`
2. **Search and filter** your imported foods
3. **Create patients** and generate AI diet charts
4. **Use food swapping** with AI #2 (The Specialist)

## 📞 **Support**

If you encounter issues:

1. **Check the error messages** in the import output
2. **Validate your CSV format** against the sample
3. **Review the troubleshooting section** above
4. **Test with the sample file** first

---

## 🚀 **Ready to Import?**

1. **Download the sample CSV**: `sample_foods.csv`
2. **Run the import command**: `python manage.py import_foods_csv sample_foods.csv --clear`
3. **Start creating AI-powered diet charts!**

**Your Ayurvedic Diet Planner is ready to revolutionize nutrition planning!** 🥗✨


