parser grammar tscn_parser;

options {   tokenVocab = tscn_lexer; }

scene: (definition | (WHITESPACE | NEWLINE))+;

definition: OPEN_BRACKET NAME (WHITESPACE|header_property)* CLOSE_BRACKET (NEWLINE definition_property)*;
header_property: NAME ASSIGNMENT value;
definition_property: NAME WHITESPACE* ASSIGNMENT WHITESPACE* value;
value: (string_value | numeric_value | boolean_value | invocation_value | jsonlike_value | array_value);
string_value: STRING_LITERAL;
numeric_value: NUMERIC_LITERAL;
boolean_value: BOOLEAN_LITERAL;
invocation_value: NAME OPEN_PAREN whitespace_or_newline* parameter_list? whitespace_or_newline* CLOSE_PAREN;
array_value: OPEN_BRACKET whitespace_or_newline* parameter_list? whitespace_or_newline* CLOSE_BRACKET;
whitespace_or_newline: WHITESPACE | NEWLINE;
parameter_list: parameter (COMMA parameter)*;
parameter: whitespace_or_newline* value whitespace_or_newline*;
jsonlike_value: OPEN_CURLY whitespace_or_newline* jsonlike_property_list? whitespace_or_newline* CLOSE_CURLY;
jsonlike_property_list: jsonlike_property (COMMA jsonlike_property)*;
jsonlike_property: whitespace_or_newline* STRING_LITERAL whitespace_or_newline* COLON whitespace_or_newline* value whitespace_or_newline*;



