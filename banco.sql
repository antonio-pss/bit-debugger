create table display (
    id SERIAL not null,
    name varchar(25) not null,
    constraint pk_display primary key (id)
);

create table frame (
    id SERIAL not null,
    text text,
    pos_x float not null,
    pos_y float not null,
    surf_path text not null,
    answer boolean,
    id_display integer not null,
    color varchar(10) default 'white',
    size numeric default 16,
    number numeric default 0,
    constraint pk_frame primary key (id),
    constraint fk_frame_display foreign key (id_display) references display (id)
);

-- Displays
insert into display (id, name)
values (1, 'Main Menu'),
       (2, 'Menu'),
       (3, 'Game Over'),
       (4, 'Victory'),
       (5, 'Choose'),
       (6, 'Tip'),
       (7, 'Question');

-- Main Menu
insert into frame (text, pos_x, pos_y, surf_path, answer, id_display, size)
values (' ', 0.5, 0.3, '..|images|displays|logos', false, 1, default),
       ('Começar', 0.5, 0.6, '..|images|displays|btn_small', false, 1, 16*2),
       ('Sair', 0.5, 0.7, '..|images|displays|btn_small', false, 1, 16*2);

-- Menu
insert into frame (text, pos_x, pos_y, surf_path, answer, id_display, size)
values (' ', 0.5, 0.3, '..|images|displays|logos', false, 2, default),
       ('Voltar', 0.5, 0.6, '..|images|displays|btn_small', false, 2, 16*2),
       ('Reiniciar', 0.5, 0.7, '..|images|displays|btn_small', false, 2, 16*2),
       ('Sair', 0.5, 0.8, '..|images|displays|btn_small', false, 2, 16*2);

-- Game Over
insert into frame (text, pos_x, pos_y, surf_path, answer, id_display)
values ('É uma pena, você perdeu todos os seus cafés, estamos sem energia para continuar. Vamos encher a  garrafa e você pode tentar novamente mais tarte. Lembre-se, aprendizado vem atráves de muitas tentativas. Se gostou, vote na gente pelo QR code. Boa sorte da próxima. Paia', 0.5, 0.5, '..|images|tela', false, 3);

-- Victory
insert into frame (text, pos_x, pos_y, surf_path, answer, id_display)
values ('Parabéns!! Você terminou nossa demo com sucesso, espero que tenha se divertido. Se gostou, vote na gente pelo QR code. Muito obrigado por ter jogado.', 0.5, 0.5, '..|images|tela', false, 4);

-- Choose
insert into frame (text, pos_x, pos_y, surf_path, answer, id_display, size)
values ('Você tem certeza?', 0.5, 0.3, '..|images|displays|btn_qlarge', false, 5, 16*3),
       ('Sim', 0.25, 0.5, '..|images|displays|btn_small', false, 5, 16*2),
       ('Não', 0.75, 0.5, '..|images|displays|btn_small', false, 5, 16*2);

-- Tips
insert into frame (text, pos_x, pos_y, surf_path, answer, id_display, number)
values ('Para jogar, você pode usar as teclas "A", "D" e  "espaço". Você também pode usar as setas do teclado. No canto superior esquerdo, estão suas vidas, representadas por cafés. No caminho, haverá inimigos; para derrotá-los, é preciso pular em suas cabeças. Também haverá desafios; se você errá-los, voltará ao início. Para sair da dica, aperte "E" novamente. Bom jogo e boa sorte.', 0.5, 0.5, '..|images|tela', false, 6, 0),
       ('Variável é um local que armazena um tipo específico de conteúdo como números inteiros, textos, números reais entre outros.', 0.5, 0.5, '..|images|tela', false, 6, 1),
       ('Temos 4 tipos de variáveis primárias na programção, são elas: Inteiro, Real, Texto, Lógico.', 0.5, 0.5, '..|images|tela', false, 6, 2);


-- Question 1
insert into frame (text, pos_x, pos_y, surf_path, answer, id_display, color, size, number)
values ('O que é uma  variável?', 0.5, 0.25, '..|images|tela', false, 7, 'red', default, 1),
       ('Local que armazena um tipo específico de valor', 0.25, 0.6, '..|images|displays|btn_qlarge', true, 7, default, 20, 1),
       ('Local que armazena só um tipo específico de valor', 0.75, 0.6, '..|images|displays|btn_qlarge', false, 7, default, 20, 1),
       ('Local que armazena só textos', 0.25, 0.8, '..|images|displays|btn_qlarge', false, 7, default, 20, 1),
       ('Local que armazena só números inteiros', 0.75, 0.8, '..|images|displays|btn_qlarge', false, 7, default, 20, 1);

-- Question 2
insert into frame (text, pos_x, pos_y, surf_path, answer, id_display, color, size, number)
values ('Quais são os tipos de variáveis que podemos ter na programação?', 0.5, 0.25, '..|images|tela', false, 7, 'red', default, 2),
       ('Inteiro, Decimal, Verdadeiro, Letra', 0.25, 0.6, '..|images|displays|btn_qlarge', false, 7, default, 20, 2),
       ('Número, Texto, Frase, Falso', 0.75, 0.6, '..|images|displays|btn_qlarge', false, 7, default, 20, 2),
       ('Inteiro, Real, Texto, Lógico', 0.25, 0.8, '..|images|displays|btn_qlarge', true, 7, default, 20, 2),
       ('Real, Lógico, Texto, Adição', 0.75, 0.8, '..|images|displays|btn_qlarge', false, 7, default, 20, 2);

