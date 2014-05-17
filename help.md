Available commands:

<>help : prints this
<>eval : evaluates a streambase expression
      
       Usage: <>eval <CEP_EXPR>
       Eg.,
                ; this returns 5
                <>eval 2+3

                ; this returns 30 (because 1^2 + 2^2 + 3^2 + 4 ^2 = 30)
                <>eval function f(a int) -> int { if a > 0 then a * a + f(a - 1) else 0 }(4)

<>sbx : execute an sbx command
      
      Usage: <>sbx <ARGS>
      Eg.,

                ; this prints a duck
                <>sbx ducky --quack

<>go away: kills the bot.


Last but not least, doctor mode.

Usage: <say whatever you want!>
