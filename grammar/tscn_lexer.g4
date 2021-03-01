lexer grammar tscn_lexer;

OPEN_BRACKET: '[';
CLOSE_BRACKET: ']';
OPEN_PAREN: '(';
CLOSE_PAREN: ')';
OPEN_CURLY: '{';
CLOSE_CURLY: '}';
COMMA: ',';
COLON: ':';
STRING_LITERAL : '"' (~('"' | '\\' ) | '\\' ('"' | '\\'))* '"';
NUMERIC_LITERAL: '-'? [0-9]+ ('.' [0-9]+)? ('e' '-'? [0-9]+)?;
BOOLEAN_LITERAL: 'true' | 'false';
NAME: [A-Za-z_][A-Za-z0-9_/]*;
ASSIGNMENT: '=';
WHITESPACE: [ \t]+;
NEWLINE: [\r\n]+;
