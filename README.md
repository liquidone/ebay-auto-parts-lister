# eBay Auto Parts Lister
<!-- Webhook test - auto-deployment system active -->

An automated system for processing auto part images and creating optimized eBay listings using AI vision and image processing.

## Features

- **Smart Image Processing**: Auto-crop, rotate, and enhance images for optimal eBay display
- **AI Part Identification**: Uses GPT-4 Vision to identify auto parts and generate descriptions
- **Market Pricing**: Intelligent pricing suggestions for quick sales
- **SEO Optimization**: Creates optimized titles and descriptions for better visibility
- **eBay Integration**: Automatically creates draft listings in your eBay account
- **Local Processing**: Everything runs on your computer for privacy and speed

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys
1. Copy `.env.template` to `.env`
2. Add your OpenAI API key for part identification
3. Add your eBay API credentials for listing creation

### 3. Run the Application
```bash
python main.py
```

### 4. Access the Web Interface
Open your browser and go to: `http://127.0.0.1:8000`

## How It Works

1. **Upload Images**: Drag and drop auto part photos into the web interface
2. **AI Processing**: The system automatically:
   - Enhances and optimizes images
   - Identifies the part using AI vision
   - Determines compatible vehicles
   - Suggests competitive pricing
   - Generates SEO-optimized listings
3. **Review & Launch**: Review the generated listings and publish to eBay

## API Keys Required

### OpenAI API Key
- Sign up at: https://platform.openai.com/
- Create an API key in your dashboard
- Add to `.env` file as `OPENAI_API_KEY`

### eBay API Keys
- Register at: https://developer.ebay.com/
- Create a new application
- Get your App ID, Dev ID, Cert ID, and User Token
- Add all keys to `.env` file

## Project Structure

```
├── main.py                 # Main FastAPI application
├── modules/
│   ├── image_processor.py  # Image processing and optimization
│   ├── part_identifier.py  # AI-powered part identification
│   └── database.py         # Local data storage
├── uploads/                # Uploaded images
├── processed/              # Processed images
├── static/                 # Static files for web interface
└── requirements.txt        # Python dependencies
```

## Image Processing Pipeline

1. **Auto-Rotation**: Detects and corrects image orientation
2. **Smart Cropping**: Focuses on the main auto part
3. **Enhancement**: Improves contrast, sharpness, and brightness
4. **Optimization**: Resizes for optimal eBay display
5. **SEO Preparation**: Optimizes for search visibility

## Part Identification Features

- Identifies specific part names and categories
- Determines compatible vehicle makes/models
- Assesses condition and market value
- Generates professional descriptions
- Creates SEO-optimized titles
- Estimates shipping costs and dimensions

## Supported Part Categories

- Engine Components
- Transmission Parts
- Brake System
- Suspension
- Electrical Components
- Body Parts
- Interior Parts
- Exhaust System
- Cooling System
- Fuel System
- Steering Components
- Drivetrain

## Tips for Best Results

1. **Image Quality**: Use well-lit, clear photos
2. **Multiple Angles**: Upload 2-3 different views of the part
3. **Part Numbers**: Include photos of any visible part numbers
4. **Clean Parts**: Clean parts photograph better and sell faster
5. **Reference Objects**: Include coins or rulers for size reference

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all API keys are correctly set in `.env`
2. **Image Processing Fails**: Check image format (JPG, PNG supported)
3. **Part Not Identified**: Try different angles or better lighting
4. **eBay Connection Issues**: Verify eBay API credentials and environment setting

### Support

For issues or questions:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure API keys are valid and have sufficient credits

## Future Enhancements

- Batch processing for multiple parts
- Advanced dimension estimation using reference objects
- Integration with additional auto parts databases
- Automated repricing based on market changes
- Mobile app for on-the-go listing creation
