class NodeMobility:
    def __init__ (self, times, locations):
        self.__times = times
        self.__locations = locations
    def get_location(self, time):
        if time in self.__times:
            index = self.__times.index(time)
            return list(self.__locations[index])
        elif time > self.__times[-1]:
            return list(self.__locations[-1])
        elif time < 0:
            # Negative time not used
            return list(self.__locations[0])
        else:
            index = 0
            for t in self.__times:
                if t > time:
                    break
                index+= 1
            interval = self.__times[index] - self.__times[index-1]
            t3 = time - self.__times[index-1]
            assert interval > 0
            return self.calculate_location (self.__locations[index-1], self.__locations[index], interval, t3)
    def calculate_location(self, p1, p2, interval, t3):
        location = []
        for i in range(len(p1)):
            location.append( p1[i] + (p2[i]-p1[i])*(t3/interval) )
        return location
    def get_wptimes(self):
        return list (self.__times)
