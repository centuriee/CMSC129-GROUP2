import os

def process_input(states, inp, char_0, char_1):
    
    current_state = "NONE"
    for state_name, state_params in states.items():
        if state_params[0] == '-':
            if current_state != "NONE":
                raise Exception("Multiple start states detected")
            current_state = state_name
            break
    
    for char in inp:
        if(char == char_0):
            current_state = states[current_state][1]
        elif(char == char_1):
            current_state = states[current_state][2]
        else:
            raise Exception("Invalid input character detected")
        
    if states[current_state][0] == '+':
        return "VALID"
    else:
        return "INVALID"
            
def main():

    working_dict = os.getcwd() + '\\Behimino_Nalasa_Plariza_Reyno_PE01\\utils\\'
    strings_txt = working_dict + "strings.txt"
    transitions_txt = working_dict + "transitions.txt"
    try:
        state_dict = {}
        with open(transitions_txt, "r", encoding="utf-8") as f: #Reads the file contents when selected
            for index, line in enumerate(f):
                if index == 0:
                    char_0, char_1 = line.replace("\n", "").split(',')
                else:
                    state_type, state_name, state_trans_0, state_trans_1 = line.replace("\n", "").split(',')
                    state_dict[state_name] = (state_type, state_trans_0, state_trans_1)

        with open(strings_txt, 'r', encoding="utf-8") as f:
            for line in f:
                result = process_input(state_dict, line.replace("\n", ""), char_0, char_1)
                print(f"{line}: {result}")
    except Exception as e:
       print(f"Error: {e}")

main()