import numpy as np
from multiagent.core import World, Agent, Landmark
from multiagent.scenario import BaseScenario
from geo_env import Geo_env
from geopandas.geoseries import GeoSeries
from shapely.geometry import Point
import datetime

class Scenario(BaseScenario):
    def make_world(self):
        world = World()
        self.es = Geo_env(coord_len=8)
        self.red = self.es.red_line
        # add agents
        world.agents = [Agent() for i in range(8)]
        for i, agent in enumerate(world.agents):
            agent.name = 'agent %d' % i
            agent.collide = False
            agent.silent = True
            agent.adversary = False
        # add landmarks
        # world.landmarks = [Landmark() for i in range(0)]
        # for i, landmark in enumerate(world.landmarks):
        #     landmark.name = 'landmark %d' % i
        #     landmark.collide = False
        #     landmark.movable = False
        # make initial conditions
        self.reset_world(world)
        return world

    def reset_world(self, world):
        # random properties for agents
        for i, agent in enumerate(world.agents):
            agent.color = np.array([0.25,0.25,0.25])
        # random properties for landmarks
        # for i, landmark in enumerate(world.landmarks):
        #     landmark.color = np.array([0.75,0.75,0.75])
        # world.landmarks[0].color = np.array([0.75,0.25,0.25])

        DNA = self.es.init_coord()

        # set random initial states
        for i,agent in enumerate(world.agents):
            agent.state.p_pos = DNA[i]
            agent.state.p_vel = np.zeros(world.dim_p)
            agent.state.c = np.zeros(world.dim_c)
        for i, landmark in enumerate(world.landmarks):
            landmark.state.p_pos = np.random.uniform(-1,+1, world.dim_p)
            landmark.state.p_vel = np.zeros(world.dim_p)

    def reward(self, agent, world):
        self.DNA = np.zeros((self.es.coord_len,2))
        for i,agent in enumerate(world.agents):
            self.DNA[i] = agent.state.p_pos
        res = self.get_reward()
        return res

    def get_reward(self):
        reward = []
        reward1,request,distance = self.es.get_fitness_matrix_double(self.DNA)
        for i in range(self.es.coord_len):
            reward1_ = reward1[i].sum() - self.es.coord_len - 1
            reward2 = self.es.in_area(self.DNA[i], self.es.buildinginf[i]["walls"]) - 1
            reward3 = self.es.house_wall_geo(self.es.buildinginf[i]["walls"]) \
                .translate(xoff=self.DNA[i][0],yoff=self.DNA[i][1]) \
                .distance(self.red).values[0] - 1
            tmp = reward1_*10 + reward2*20 - float(reward3)
            if tmp == 0:
                tmp = 100
            reward.append(tmp)
        if sum(reward) == 100*self.es.coord_len:
            print(self.DNA.tolist())
            with open("DDPG-RA-%d.txt", "a") as f:
                nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(nowTime + '  ' + str(self.DNA.tolist()) + '\n')
        return reward




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

        e = float(GeoSeries(Point(agent.state.p_pos)).distance(self.red).values[0])
        ii = self.es.house_wall_geo(self.es.buildinginf[int(agent.name.split()[1])]["walls"]) \
            .translate(xoff=agent.state.p_pos[0],yoff=agent.state.p_pos[1]) \
            .distance(self.red).values[0]

        return np.concatenate([agent.state.p_vel] + other_pos + other_vel + [[e]] + [[ii]])
