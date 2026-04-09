# Download remaining product images - run from your local terminal
# The Shopify CDN URLs are unique, so you may need to inspect each product page
# to get the actual image URL

# Missing images we know:
# - pre-workout.png (PRE-WORKOUT EXTREME)
# - caffeine.png (CAFFEINE BOOST)
# - pump.png (PUMP ENHANCER)
# - l-carnitine.png (L-CARNITINE)
# - fat-burner.png (FAT BURNER)
# - multivitamin.png (MULTIVITAMIN)
# - omega3.png (OMEGA-3)
# - vitamin-d.png (VITAMIN D3)

# Generic download command template:
# Invoke-WebRequest -Uri "https://needsupps.site/cdn/shop/files/YOUR_IMAGE_NAME.png" -OutFile "C:\Users\viren\Downloads\ai-website-cloner-template-master\ai-website-cloner-template-master\public\images\products\YOUR_IMAGE_NAME.png"

# To find correct URLs:
# 1. Visit https://needsupps.site/collections/pre-training
# 2. Right-click each product image -> Copy Image Address
# 3. Replace spaces with hyphens in filename

Write-Host "Please manually download missing images from the product pages."
Write-Host "Common URLs follow Shopify pattern: https://needsupps.site/cdn/shop/files/[product-name].png"