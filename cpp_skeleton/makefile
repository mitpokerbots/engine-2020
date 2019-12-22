CXXFLAGS = -Wall -std=c++11
LDLIBS = -lboost_system -lboost_program_options -lpthread

pokerbot: main.cpp player.cpp player.hpp skeleton/bot.hpp skeleton/runner.cpp skeleton/runner.hpp skeleton/states.cpp skeleton/states.hpp skeleton/actions.cpp skeleton/actions.hpp
	g++ $(CXXFLAGS) -o pokerbot main.cpp player.cpp skeleton/runner.cpp skeleton/states.cpp skeleton/actions.cpp $(LDLIBS)

clean:
	rm pokerbot