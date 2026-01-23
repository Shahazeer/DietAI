#!/usr/bin/env python3
"""
Build nutrition knowledge base for RAG
Populates ChromaDB with curated nutrition facts and food-health relationships
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import get_vector_store
import json

# Curated nutrition knowledge base
# This contains verified information about foods and their health benefits
NUTRITION_KNOWLEDGE = [
    # GRAINS & CEREALS
    {
        "food_name": "Oats",
        "category": "Grain",
        "text": "Oats - High fiber (10g/100g), low GI. Benefits: Lowers cholesterol, stabilizes blood sugar, heart health. Good for diabetes, heart disease, weight loss. Common dishes: Oatmeal, overnight oats.",
        "good_for": ["diabetes", "heart disease", "weight loss", "cholesterol"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Brown Rice",
        "category": "Grain",
        "text": "Brown Rice - Whole grain, fiber 3.5g/100g. Benefits: Sustained energy, digestive health, blood sugar control. Good for diabetes, digestion. Common dishes: Rice bowls, pulao.",
        "good_for": ["diabetes", "digestion", "general wellness"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Quinoa",
        "category": "Grain",
        "text": "Quinoa - Complete protein, high fiber. Benefits: Muscle building, blood sugar control, gluten-free. Good for diabetes, weight management, celiac. Common dishes: Quinoa bowls, salads.",
        "good_for": ["diabetes", "weight loss", "muscle building"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Whole Wheat",
        "category": "Grain",
        "text": "Whole Wheat - Fiber 12g/100g. Benefits: Digestive health, sustained energy. Good for general wellness. Common dishes: Chapati, roti, bread.",
        "good_for": ["digestion", "general wellness"],
        "diet_type": "vegetarian"
    },
    
    # LEGUMES & PULSES
    {
        "food_name": "Chickpeas",
        "category": "Legume",
        "text": "Chickpeas (Chana) - Protein 19g/100g, fiber 17g. Benefits: Blood sugar control, weight management, heart health. Good for diabetes, weight loss. Common dishes: Chana masala, hummus, salads.",
        "good_for": ["diabetes", "weight loss", "heart disease"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Lentils",
        "category": "Legume",
        "text": "Lentils (Dal) - Protein 25g/100g, folate rich. Benefits: Heart health, blood sugar control, digestive health. Good for diabetes, heart disease, anemia. Common dishes: Dal tadka, sambar, soup.",
        "good_for": ["diabetes", "heart disease", "anemia"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Kidney Beans",
        "category": "Legume",
        "text": "Kidney Beans (Rajma) - High protein and fiber. Benefits: Blood sugar control, heart health. Good for diabetes, weight loss. Common dishes: Rajma curry, chili.",
        "good_for": ["diabetes", "weight loss", "heart disease"],
        "diet_type": "vegetarian"
    },
    
    # VEGETABLES
    {
        "food_name": "Spinach",
        "category": "Vegetable",
        "text": "Spinach (Palak) - Iron rich, low calorie. Benefits: Blood building, eye health, bone health. Good for anemia, weight loss, bone health. Common dishes: Palak paneer, saag, salads.",
        "good_for": ["anemia", "weight loss", "bone health"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Broccoli",
        "category": "Vegetable",
        "text": "Broccoli - Vitamin C, fiber, antioxidants. Benefits: Cancer prevention, immune support, heart health. Good for heart disease, immunity. Common dishes: Stir fry, soups, salads.",
        "good_for": ["heart disease", "immunity", "cancer prevention"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Bitter Gourd",
        "category": "Vegetable",
        "text": "Bitter Gourd (Karela) - Blood sugar reducer. Benefits: Diabetes management, liver health. Good for diabetes, liver problems. Common dishes: Karela sabzi, juice.",
        "good_for": ["diabetes", "liver health"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Bottle Gourd",
        "category": "Vegetable",
        "text": "Bottle Gourd (Lauki) - Low calorie, hydrating. Benefits: Weight loss, cooling, digestive health. Good for weight loss, digestion, general wellness. Common dishes: Lauki sabzi, soup.",
        "good_for": ["weight loss", "digestion", "general wellness"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Cauliflower",
        "category": "Vegetable",
        "text": "Cauliflower (Gobi) - Low carb, vitamin C. Benefits: Weight management, immunity. Good for weight loss, diabetes. Common dishes: Gobi masala, rice alternatives.",
        "good_for": ["weight loss", "diabetes"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Tomato",
        "category": "Vegetable",
        "text": "Tomato - Lycopene rich, low calorie. Benefits: Heart health, skin health, cancer prevention. Good for heart disease, skin health. Common dishes: Curries, salads, soups.",
        "good_for": ["heart disease", "skin health"],
        "diet_type": "vegetarian"
    },
    
    # FRUITS
    {
        "food_name": "Apple",
        "category": "Fruit",
        "text": "Apple - Fiber rich, pectin. Benefits: Heart health, digestive health, blood sugar control Good for diabetes (in moderation), heart disease. Common: Fresh, salads.",
        "good_for": ["diabetes", "heart disease", "digestion"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Banana",
        "category": "Fruit",
        "text": "Banana - Potassium 358mg/100g. Benefits: Energy, heart health, digestive health. Good for general wellness, exercise recovery. Common: Fresh, smoothies.",
        "good_for": ["general wellness", "heart disease"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Berries",
        "category": "Fruit",
        "text": "Berries (Strawberry, Blueberry) - Antioxidants, low GI. Benefits: Blood sugar control, heart health, brain health. Good for diabetes, heart disease. Common: Fresh, smoothies.",
        "good_for": ["diabetes", "heart disease", "brain health"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Orange",
        "category": "Fruit",
        "text": "Orange - Vitamin C rich. Benefits: Immunity, skin health, iron absorption. Good for immunity, anemia. Common: Fresh juice, fruit.",
        "good_for": ["immunity", "anemia", "skin health"],
        "diet_type": "vegetarian"
    },
    
    # DAIRY
    {
        "food_name": "Greek Yogurt",
        "category": "Dairy",
        "text": "Greek Yogurt - High protein, probiotics. Benefits: Gut health, protein source, bone health. Good for digestion, weight loss, bone health. Common: Breakfast bowls, smoothies.",
        "good_for": ["digestion", "weight loss", "bone health"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Paneer",
        "category": "Dairy",
        "text": "Paneer - Protein 18g/100g, calcium rich. Benefits: Muscle building, bone health. Good for weight training, bone health. Common dishes: Paneer tikka, curry.",
        "good_for": ["muscle building", "bone health"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Low-fat Milk",
        "category": "Dairy",
        "text": "Low-fat Milk - Calcium, vitamin D. Benefits: Bone health, protein. Good for bone health, general wellness. Common: Beverages, cereals.",
        "good_for": ["bone health", "general wellness"],
        "diet_type": "vegetarian"
    },
    
    # NUTS & SEEDS
    {
        "food_name": "Almonds",
        "category": "Nuts",
        "text": "Almonds - Healthy fats, vitamin E. Benefits: Heart health, brain health, blood sugar control. Good for diabetes, heart disease. Common: Snacks, toppings.",
        "good_for": ["diabetes", "heart disease", "brain health"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Walnuts",
        "category": "Nuts",
        "text": "Walnuts - Omega-3 fatty acids. Benefits: Brain health, heart health, inflammation reduction. Good for heart disease, brain health. Common: Snacks, salads.",
        "good_for": ["heart disease", "brain health"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Chia Seeds",
        "category": "Seeds",
        "text": "Chia Seeds - Omega-3, fiber 34g/100g. Benefits: Heart health, digestive health, blood sugar control. Good for diabetes, heart disease. Common: Puddings, smoothies.",
        "good_for": ["diabetes", "heart disease", "digestion"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Flax Seeds",
        "category": "Seeds",
        "text": "Flax Seeds - Omega-3, lignans. Benefits: Heart health, hormone balance, digestion. Good for heart disease, hormone health. Common: Ground in smoothies, cereals.",
        "good_for": ["heart disease", "hormone health"],
        "diet_type": "vegetarian"
    },
    
    # PROTEINS (NON-VEG)
    {
        "food_name": "Chicken Breast",
        "category": "Meat",
        "text": "Chicken Breast - Lean protein 31g/100g, low fat. Benefits: Muscle building, weight loss. Good for weight loss, muscle building. Common dishes: Grilled chicken, curry.",
        "good_for": ["weight loss", "muscle building"],
        "diet_type": "non-veg"
    },
    {
        "food_name": "Salmon",
        "category": "Fish",
        "text": "Salmon - Omega-3 EPA/DHA, protein 20g/100g. Benefits: Heart health, brain health, inflammation reduction. Good for heart disease, brain health. Common dishes: Grilled, baked.",
        "good_for": ["heart disease", "brain health"],
        "diet_type": "non-veg"
    },
    {
        "food_name": "Eggs",
        "category": "Protein",
        "text": "Eggs - Complete protein, choline. Benefits: Muscle building, brain health, eye health. Good for general wellness, muscle building. Common dishes: Boiled, scrambled, omelette.",
        "good_for": ["muscle building", "brain health", "general wellness"],
        "diet_type": "eggetarian"
    },
    {
        "food_name": "Tuna",
        "category": "Fish",
        "text": "Tuna - Lean protein, omega-3. Benefits: Heart health, weight loss. Good for heart disease, weight loss. Common dishes: Salads, sandwiches.",
        "good_for": ["heart disease", "weight loss"],
        "diet_type": "non-veg"
    },
    
    # HERBS & SPICES
    {
       "food_name": "Turmeric",
        "category": "Spice",
        "text": "Turmeric (Haldi) - Curcumin, anti-inflammatory. Benefits: Inflammation reduction, immunity, joint health. Good for arthritis, inflammation, immunity. Common: Curries, milk.",
        "good_for": ["arthritis", "inflammation", "immunity"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Ginger",
        "category": "Spice",
        "text": "Ginger (Adrak) - Anti-inflammatory, digestive aid. Benefits: Nausea relief, digestion, immunity. Good for digestion, nausea, immunity. Common: Tea, curries.",
        "good_for": ["digestion", "nausea", "immunity"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Garlic",
        "category": "Spice",
        "text": "Garlic (Lehsun) - Allicin, blood pressure reducer. Benefits: Heart health, immunity, cholesterol. Good for heart disease, high blood pressure. Common: Curries, sauces.",
        "good_for": ["heart disease", "high blood pressure", "cholesterol"],
        "diet_type": "vegetarian"
    },
    {
        "food_name": "Fenugreek",
        "category": "Spice",
        "text": "Fenugreek (Methi) - Blood sugar control, fiber. Benefits: Diabetes management, digestion, lactation. Good for diabetes, digestion. Common: Seeds in curries, leaves in sabzi.",
        "good_for": ["diabetes", "digestion"],
        "diet_type": "vegetarian"
    },
    
    # BEVERAGES
    {
        "food_name": "Green Tea",
        "category": "Beverage",
        "text": "Green Tea - Antioxidants, metabolism boost. Benefits: Weight loss, heart health, brain health. Good for weight loss, heart disease. Common: Hot tea.",
        "good_for": ["weight loss", "heart disease", "brain health"],
        "diet_type": "vegetarian"
    },
]


def main():
    print("=" * 60)
    print("🏗️ BUILDING NUTRITION KNOWLEDGE BASE")
    print("=" * 60)
    
    vector_store = get_vector_store()
    
    # Check if already populated
    current_count = vector_store.get_count()
    if current_count > 0:
        print(f"\n⚠️ Knowledge base already has {current_count} documents.")
        response = input("Clear and rebuild? (yes/no): ")
        if response.lower() == 'yes':
            vector_store.clear()
            print("✅ Cleared existing knowledge base")
        else:
            print("Keeping existing data")
            return
    
    print(f"\n📊 Adding {len(NUTRITION_KNOWLEDGE)} nutrition facts...")
    
    # Prepare documents and metadata
    documents = [item["text"] for item in NUTRITION_KNOWLEDGE]
    metadatas = [
        {
            "food_name": item["food_name"],
            "category": item["category"],
            "good_for": ",".join(item["good_for"]),
            "diet_type": item["diet_type"]
        }
        for item in NUTRITION_KNOWLEDGE
    ]
    ids = [f"food_{i}" for i in range(len(NUTRITION_KNOWLEDGE))]
    
    # Add to vector store
    vector_store.add_documents(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"\n✅ Knowledge base built successfully!")
    print(f"📈 Total documents: {vector_store.get_count()}")
    
    # Test retrieval
    print("\n🧪 Testing retrieval...")
    test_query = "foods good for diabetes"
    results = vector_store.query(test_query, n_results=5)
    
    print(f"\nQuery: '{test_query}'")
    print("Top 5 results:")
    for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
        print(f"{i}. {meta['food_name']} - {doc[:80]}...")
    
    print("\n🎉 Knowledge base ready for RAG!")
    print("\nNext steps:")
    print("1. The diet planner will now use this knowledge")
    print("2. You can expand this knowledge base by editing this script")
    print("3. Run this script again to rebuild with new data")


if __name__ == "__main__":
    main()
