import requests
import json
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

# Use localhost instead of ngrok
api_url = "http://localhost:8000/process"

test_data = [
	{
		"audio_url": "https://pxakjsagltrtmcwagdlw.supabase.co/storage/v1/object/public/audio/9a9d9d01-5b97-4e38-a7f7-a68b20a14cb1.mp3?",
		"lyrics": """
			[Verse]
			Dust off the shoulders, heavyweight soldier
			Heart like boulders, world gettin' colder
			Step through the struggle, hustlin' jumble
			Fell nine times, tenth time rubble

			[Chorus]
			Keep it movin', never losin'
			Findin' light in all confusion
			Challenges turnin', I'm learnin'
			Power in the fire, keep it burnin'

			[Verse 2]
			Crumblin' pressure, but I measure up
			Champ with the belt, ain't no runner-up
			Storms bring the thunder, I ain't hidin' under
			Phoenix from the ashes, rises stronger

			[Bridge]
			Brick by brick, buildin' this empire
			Doubt fuels the flame, feeds my fire
			Turn the pain to gain, break the chain
			Mind over matter, fight through the rain

			[Verse 3]
			Life's full of tests, I ace 'em all
			Standin' tall in the face of my fall
			Resilient spirit, hear it, feel it
			Every hit taken, bars reveal it

			[Chorus]
			Keep it movin', never losin'
			Findin' light in all confusion
			Challenges turnin', I'm learnin'
			Power in the fire, keep it burnin'
		"""
	},
	{
		"audio_url": "https://pxakjsagltrtmcwagdlw.supabase.co/storage/v1/object/public/audio/f0a6e037-2938-4428-8a6b-9c839c583ef1.mp3?",
		"lyrics": """
			[Verse]
			I was born in the shadow, 'neath the Tennessee pines,
			With a dream and a whisper, echoing through hard times.
			Mama said, "Boy, don't you ever give in,
			The fire in your heart, that's where you begin."

			[Verse 2]
			Daddy left early, and the bills piled high,
			But I kept on pushin' with my eyes to the sky.
			Spent nights in the fields, talkin' to the moon,
			Believin' deep down I'd break free soon.

			[Chorus]
			I am destined for greatness, no matter the odds,
			With the stars as my beacon, and faith as my guard.
			Through the storms and the sorrows, I'll rise above,
			'Cause in my blood runs the strength of love.

			[Verse 3]
			Worked on the railroads, sang songs in the bars,
			Wrote my story in the dust of old cars.
			Took every hit, but I never stayed down,
			This heart's a warrior, I ain't leavin' this town.

			[Verse 4]
			They called me crazy, said, "Boy, you'll fall,"
			But I looked 'em in the eye, stood ten feet tall.
			For every dark night, there's a dawn of gold,
			My spirit's unbroken, my soul ain't been sold.

			[Chorus]
			I am destined for greatness, no matter the odds,
			With the stars as my beacon, and faith as my guard.
			Through the storms and the sorrows, I'll rise above,
			'Cause in my blood runs the strength of love.
		"""
	},
	{
		"audio_url": "https://pxakjsagltrtmcwagdlw.supabase.co/storage/v1/object/public/audio/1044bb8d-2227-42d5-a259-116c74528ec5.mp3?",
		"lyrics": """
			[Verse]
			Wake up every morning feeling like a dream
			밤하늘에 별처럼 반짝이는 scheme
			Got my vision board and a million-dollar gleam
			현실로 바꿀 거야 life is never what it seems

			[Chorus]
			I am wealthy 풍요가 내 안에 있어요
			Money flows to me 나는 그렇다고 믿어요
			Cash in hand 내가 다 가질래
			계속 이루어지고 있어 내가 꿈꿨던 세계

			[Verse 2]
			Credit cards and dollar bills they multiply
			어디 가든 밝게 빛나 like a firefly
			Dreams are turning real and I'm aiming high
			날아오를 거야 저 높이 저 하늘 위로 fly

			[Chorus]
			I am wealthy 풍요가 내 안에 있어요
			Money flows to me 나는 그렇다고 믿어요
			Cash in hand 내가 다 가질래
			계속 이루어지고 있어 내가 꿈꿨던 세계

			[Bridge]
			Manifesting everything cause I believe it’s true
			이블록 안에서 보고 또 보며 I grew
			Now I see the magic happening fortune's overdue
			내 마음속에 간직해 내가 이룬 꿈의 문

			[Chorus]
			I am wealthy 풍요가 내 안에 있어요
			Money flows to me 나는 그렇다고 믿어요
			Cash in hand 내가 다 가질래
			계속 이루어지고 있어 내가 꿈꿨던 세계
		"""
	},
	{
		"audio_url": "https://pxakjsagltrtmcwagdlw.supabase.co/storage/v1/object/public/audio/a1cd8046-6e2a-4b59-8417-f8ff9790c5ab.mp3?",
		"lyrics": """
			[Verse]
			I saw you dancing in the sun
			Your laughter sparkling like the sea
			With every step my heart was done
			Could this be destiny and me

			[Verse 2]
			Sand between our toes so free
			Waves were crashing to our beat
			Underneath this big palm tree
			Our future felt so sweet

			[Chorus]
			Amor en la playa mi amor
			We'll dance until the night implores
			The rhythm pulls us close for sure
			Two hearts united ever more

			[Verse 3]
			Your eyes like stars in daylight’s glow
			As the sun began to fade
			With every smile the world would know
			A love that wouldn't be swayed

			[Bridge]
			The ocean sings a melody
			Of promises and new tomorrows
			We'll surf the waves just you and me
			No need for any sorrows

			[Chorus]
			Amor en la playa mi amor
			We'll dance until the night implores
			The rhythm pulls us close for sure
			Two hearts united ever more
		"""
	},
	{
		"audio_url": "https://cdn1.suno.ai/412fe667-625d-4e0f-b4a3-1627dd45b299.mp3",
		"lyrics": """
			Dogs barking.
			Feet hurt.
			Still dancing.
			Can’t stop.

			12 o’clock.
			6 a.m.
			Dogs barking
			Go again.

			Barking.
			Hurting.
			Barking.
			Need chair pants.
		"""
	},
	{
		"audio_url": "https://cdn1.suno.ai/89fdb218-acb3-4327-a40e-41b09e3473ab.mp3",
		"lyrics": """
			Chant (repeated sparingly):
			Dogs barking.
			Feet hurt.
			Still dancing.
			Can’t stop.

			Breakdown (low, distorted whispers):
			12 o’clock.
			6 a.m.
			Dogs barking
			Go again.

			Build (robotic, pulsing):
			Barking.
			Hurting.
			Barking.
			Need chair pants.

			Drop (heavily distorted, layered):
			Barking.
			Now it's time
			To go
			To Berghain.
		"""
	},
]

def process_test_data():
    for i, data in enumerate(test_data, 1):
        try:
            logging.info(f"\n=== Processing Test Case {i}/{len(test_data)} ===")
            logging.info(f"Sending request with audio URL: {data['audio_url']}")
            logging.info(f"Lyrics length: {len(data['lyrics'])} characters")
            
            start_time = time.time()
            response = requests.post(api_url, json=data)
            processing_time = time.time() - start_time
            
            logging.info(f"Response Status Code: {response.status_code}")
            logging.info(f"Processing Time: {processing_time:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                logging.info("Response received successfully:")
                logging.info(json.dumps(result, indent=2))
            else:
                logging.error(f"Error response: {response.text}")
            
            # Add a small delay between requests to avoid overwhelming the server
            time.sleep(1)
            
        except Exception as e:
            logging.error(f"Error processing test case {i}: {str(e)}")
            continue
        
        logging.info("=" * 50 + "\n")

if __name__ == "__main__":
    logging.info("Starting test run...")
    process_test_data()
    logging.info("Test run completed.")