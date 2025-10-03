from .stt import stt

def user_input(holder, mode='gpu'):
    user_input = input(holder).strip()

    if user_input:
        text = user_input
    else:
        text = stt(mode)
        
    # no text input
    #return stt()
    
    return text