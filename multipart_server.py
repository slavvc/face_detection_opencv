#!/usr/bin/env python

import asyncio as aio
from aiohttp import web
from PIL import Image, ImageDraw
import io, time
import imageio as iio
import argparse

def image_to_bytes(im):
    bts = io.BytesIO()
    im.save(bts, 'jpeg')
    return bts.getvalue()

# def image(i):
#     im = Image.new('RGB', (200,200))
#     draw = ImageDraw.Draw(im)
#     x = 100-abs(i%200-100)
#     draw.rectangle((x, 50, 100+x-1, 149))
#     del draw
#     bts = image_to_bytes(im)
#     del im
#     return bts

current_video_frame = None
connection_events = []

async def video():
    global config, current_video_frame, connection_events
    if config.dir is not None:
        import os
        mk_frames = lambda:(
            iio.imread(os.path.join(config.dir,fn))
            for fn in sorted(os.listdir(config.dir))
        )
    else:
        mk_frames = lambda:iio.get_reader(config.file)

    basetime = time.time()
    while True:
        frames = mk_frames()
        for i, frame in enumerate(frames):
            dt = time.time() - basetime
            basetime += dt

            im = Image.fromarray(frame)
            del current_video_frame
            current_video_frame = (i, im)
            for event in connection_events:
                event.set()
            await aio.sleep(max(1/config.fps - dt, 0.001))

async def stream(req):
    global connection_events
    boundary = 'whatever'
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'multipart/x-mixed-replace;boundary={}'.format(boundary)
        }
    )
    await response.prepare(req)

    event = aio.Event()
    connection_events.append(event)
    while True:

        await response.write(b'--%s\n'%boundary.encode())
        await response.write(b'Content-Type: image/jpeg\n')

        image = current_video_frame[1]
        n = current_video_frame[0]
        data = image_to_bytes(image)

        await response.write(b'Content-Length: %d\n\n'%len(data))
        await response.write(data+b'\n\n')
        await event.wait()
        event.clear()
    return response

async def root(req):
    res = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'text/html'
        }
    )
    await res.prepare(req)
    await res.write(b'''\
<html>
    <head>
        <title>Video Stream</title>
    </head>
    <body>
        <img src="/video" />
    </body>
</html>'''
    )
    return res

def parse_args():
    parser = argparse.ArgumentParser(description='video stream server')
    parser.add_argument('-fps', default=20, type=int, action='store')
    parser.add_argument('-port', default=8080, type=int, action='store')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-dir', action='store', help='directory with images')
    group.add_argument('-file', action='store', help='video file name')
    return parser.parse_args()

if __name__ == '__main__':

    config = parse_args()

    loop = aio.get_event_loop()
    loop.create_task(video())

    app = web.Application()
    app.add_routes([
        web.get('/', root),
        web.get('/video', stream)
    ])

    web.run_app(app, host='0.0.0.0', port=config.port)
