import asyncio
from frame_sdk import Frame

import boto3
from datetime import datetime
import json


async def main():
    async with Frame() as frame:

        #record audio for 7 seconds 
        await frame.bluetooth.send_lua("frame.display.text('Recording starts', 1,1);frame.display.show()")
        await frame.microphone.save_audio_file(filename="audio.wav", max_length_in_seconds=7) 
        
        await frame.bluetooth.send_lua("frame.display.text('Analyzing tone', 1,1);frame.display.show()")
     
        tone_intensity = GetToneIntensity("audio.wav")

        # for nice sounding tone show 'Green' on frame
        if tone_intensity <4: 
            await frame.bluetooth.send_lua("frame.display.text('Green', 1,1);frame.display.show()")
            
        # for neutral sounding tone show 'Yellow' on frame    
        elif tone_intensity < 7:                            
            await frame.bluetooth.send_lua("frame.display.text('Yellow', 1,1);frame.display.show()")

        # for rude sounding tone show 'Red' on frame
        else:                
            await frame.bluetooth.send_lua("frame.display.text('Red', 1,1);frame.display.show()")


def GetToneIntensity(audio_file):       
        # Use your AWS credentials (for best practice put the credentials in separate file)
        aws_access_key = '??'
        aws_secret_key = '??'
        aws_region = '??'
        
        user = "user-frame"
        timestamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

        lambda_function_name = '??' #put your aws lambda function name

        # Create an AWS S3 client
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)

        # Specify your S3 bucket and the local path to your audio file
        bucket_name = '??' #put your aws s3 bucket name
        local_file_path = audio_file

        # Upload the file
        s3.upload_file(local_file_path, bucket_name, user + '/' + timestamp + '.wav')
        
        #invoke aws lambda function 
        payload = { "user" : user, "timestamp" : timestamp }

        # Create an lambda client
        lambda_client = boto3.client('lambda', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)

        response = lambda_client.invoke(FunctionName=lambda_function_name, InvocationType='RequestResponse', Payload=json.dumps(payload))

        # Parse the response
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))

        tone_intensity = int(response_payload['tone intensity'])

        return tone_intensity


asyncio.run(main())
