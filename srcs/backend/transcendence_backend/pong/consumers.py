import json
import asyncio
import math
from logging import Logger
from typing import Literal

from channels.generic.websocket import AsyncWebsocketConsumer

logger = Logger(__name__)


dir_left: Literal["up", "down", "stop"] = 'stop'
dir_right: Literal["up", "down", "stop"] = 'stop'


class PongConsumer(AsyncWebsocketConsumer):
	task: asyncio.Task | None = None
	x = 50
	y = 50
	angle = 45
	platform_1 = 40
	platform_2 = 40
	score_1 = 10
	score_2 = 10
	p1_change = False
	p2_change = False
	score_change = False

	async def connect(self):
		if len(self.channel_layer.groups.get('game', {}).keys()) < 2:
			await self.channel_layer.group_add('game', self.channel_name)
			await self.accept()
		if len(self.channel_layer.groups.get('game', {}).keys()) == 2:
			await self.send(json.dumps({'side':'right'}))
			self.task = asyncio.ensure_future(self.send_updates())

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard('game', self.channel_name)
		if (self.task):
			self.task.cancel()
			self.task = None

	async def receive(self, text_data):
		global dir_left, dir_right
		text_data_json = json.loads(text_data)
		message = text_data_json["message"]
		if text_data_json.get("d", "left") == 'left':
			if message == 'up':
				dir_left = "up"
			elif message == 'down':
				dir_left = "down"
			elif message == "stop":
				dir_left = "stop"
		else:
			if message == 'up':
				dir_right = "up"
			elif message == 'down':
				dir_right = "down"
			elif message == "stop":
				dir_right = "stop"

	async def move(self):
		self.x += math.cos(self.angle)
		self.y += math.sin(self.angle)
		if dir_left == 'up' and self.platform_1 > 0:
			self.platform_1 -= 2
			self.p1_change = True
		elif dir_left == 'down' and self.platform_1 < 80:
			self.platform_1 += 2
			self.p1_change = True
		if dir_right == 'up' and self.platform_2 > 0:
			self.platform_2 -= 2
			self.p2_change = True
		elif dir_right == 'down' and self.platform_2 < 80:
			self.platform_2 += 2
			self.p2_change = True

	async def check_collisions(self):
		if self.x <= 1:
			if self.platform_1 - 1 < self.y < self.platform_1 + 21:
				self.angle = self.angle - 180
				self.score_1 += 1
			else:
				self.x = 97
				self.score_1 -= 1
			self.score_change = True
		elif self.x >= 99:
			if self.platform_2 - 1 < self.y < self.platform_2 + 21:
				self.angle = self.angle - 180
				self.score_2 += 1
			else:
				self.x = 3
				self.score_2 -= 1
			self.score_change = True
		elif self.y <= 1 or self.y >= 99:
			self.angle = -self.angle

	async def send_updates(self):
		while True:
			await self.check_collisions()
			await self.move()
			data = {
				'x': round(self.x, 2),
              	'y': round(self.y, 2),
			}
			if self.p1_change:
				data['p1'] = int(self.platform_1)
			if self.p2_change:
				data['p2'] = int(self.platform_2)
			if self.score_change:
				data.update({
					's1': self.score_1,
					's2': self.score_2,
				})
			await self.channel_layer.group_send(
				'game',
       			{
              		"type": "game.update",
              		"text": json.dumps(data)
				}
          	)
			self.p1_change = False
			self.p2_change = False
			self.score_change = False
			await asyncio.sleep(0.01)
   
	async def game_update(self, event):
		await self.send(text_data=event["text"])
