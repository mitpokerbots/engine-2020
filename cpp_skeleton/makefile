CXXFLAGS = -Wall -std=c++11
LDLIBS = -lboost_system -lpthread

pokerbot: main.o
	g++ $(CXXFLAGS) -o pokerbot $(LDLIBS) main.o player.o skeleton/runner.o skeleton/states.o skeleton/actions.o

main.o: main.cpp player.o skeleton/runner.o
	g++ $(CXXFLAGS) -o main.o -c main.cpp

player.o: player.cpp player.hpp skeleton/bot.hpp skeleton/states.o skeleton/actions.o
	g++ $(CXXFLAGS) -o player.o -c player.cpp

skeleton/runner.o: skeleton/runner.cpp skeleton/runner.hpp skeleton/bot.hpp skeleton/states.o skeleton/actions.o
	g++ $(CXXFLAGS) -o skeleton/runner.o -c skeleton/runner.cpp

skeleton/states.o: skeleton/states.cpp skeleton/states.hpp skeleton/actions.o
	g++ $(CXXFLAGS) -o skeleton/states.o -c skeleton/states.cpp

skeleton/actions.o: skeleton/actions.cpp skeleton/actions.hpp
	g++ $(CXXFLAGS) -o skeleton/actions.o -c skeleton/actions.cpp

clean:
	rm pokerbot main.o player.o skeleton/runner.o skeleton/states.o skeleton/actions.o