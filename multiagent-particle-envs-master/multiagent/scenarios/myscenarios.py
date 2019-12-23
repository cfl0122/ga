import numpy as np
from multiagent.core import World, Agent, Landmark
from multiagent.scenario import BaseScenario
from geo_env import Geo_env
from geopandas.geoseries import GeoSeries
from shapely.geometry import Point
import datetime
from house_multi_redline_data2_3 import red_line_total

class Scenario(BaseScenario):
    def make_world(self):
        world = World()
        world.es = Geo_env(coord_len=8,red_line_total=red_line_total)
        world.red = world.es.red_line
        world.red_init = world.red
        world.norm = [(world.es.red_line_maxx-world.es.red_line_minx),(world.es.red_line_maxy-world.es.red_line_miny)]

        # add agents
        world.agents = [Agent() for i in range(world.es.coord_len)]
        for i, agent in enumerate(world.agents):
            agent.name = 'agent %d' % i
            agent.index = i
            agent.collide = False
            agent.silent = True
            agent.adversary = False
            agent.color = np.array([0.25,0.25,0.25])
        self.reset_world(world)
        return world

    def reset_world(self, world):

        world.red = world.es.red_line = world.es.red_line_total[np.random.randint(0,10)] \
            .translate(xoff=np.random.normal(0,1000,1),yoff=np.random.normal(0,300,1)) \
            .rotate(np.random.uniform(0,360,1))

        world.es.red_line_minx, world.es.red_line_miny, world.es.red_line_maxx, world.es.red_line_maxy = \
            world.es.red_line.bounds.values[0]
        world.norm = [(world.es.red_line_maxx-world.es.red_line_minx),(world.es.red_line_maxy-world.es.red_line_miny)]

        world.DNA = world.es.init_coord()
        # set random initial states
        for i,agent in enumerate(world.agents):
            agent.state.p_pos = world.DNA[i] / world.norm
            agent.state.p_vel = np.zeros(world.dim_p)
            agent.state.c = np.zeros(world.dim_c)
        for i, landmark in enumerate(world.landmarks):
            landmark.state.p_pos = np.random.uniform(-1,+1, world.dim_p)
            landmark.state.p_vel = np.zeros(world.dim_p)


    def reward(self,agent,world):

        reward1 = world.reward_distance[agent.index].sum() - world.es.coord_len + 1
        reward2 = world.es.in_area(agent.state.p_pos*world.norm, world.es.buildinginf[agent.index]["walls"]) - 1
        reward3 = world.es.house_wall_geo(world.es.buildinginf[agent.index]["walls"]) \
            .translate(xoff=agent.state.p_pos[0] * world.norm[0], yoff=agent.state.p_pos[1] * world.norm[1]) \
            .distance(world.red).values[0]
        res = reward1*10 + reward2*50 - float(reward3)
        if res == 0:
            # print('agent', agent.index)
            res = 100
        return res




    def observation(self, agent, world):
        # get positions of all entities in this agent's reference frame
        entity_pos = []
        for entity in world.landmarks:
            entity_pos.append(entity.state.p_pos - agent.state.p_pos)

        other_pos = []
        other_vel = []
        for other in world.agents:
            if other is agent: continue
            other_pos.append(other.state.p_pos - agent.state.p_pos)
            if not other.adversary:
                other_vel.append(other.state.p_vel)

        e = float(GeoSeries(Point(agent.state.p_pos * world.norm)).distance(world.red).values[0])
        ii = world.es.house_wall_geo(world.es.buildinginf[agent.index]["walls"]) \
            .translate(xoff=agent.state.p_pos[0] * world.norm[0],yoff=agent.state.p_pos[1] * world.norm[1]) \
            .distance(world.red).values[0]


        return np.concatenate([agent.state.p_vel] + other_pos + other_vel + [[e]] + [[ii]])
