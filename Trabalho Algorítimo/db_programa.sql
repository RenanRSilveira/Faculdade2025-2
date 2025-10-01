CREATE DATABASE IF NOT EXISTS distribuidora CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE distribuidora;

-- Estado
CREATE TABLE estado (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sigla CHAR(2) NOT NULL
);

ALTER TABLE estado ADD CONSTRAINT uq_estado_sigla UNIQUE (sigla);
ALTER TABLE estado ADD CONSTRAINT uq_estado_nome UNIQUE (nome);




-- Cidade
CREATE TABLE cidade (
    id_cidade INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    id_estado INT NOT NULL,
    FOREIGN KEY (id_estado) REFERENCES estado(id_estado) ON DELETE CASCADE
);

-- Endereço
CREATE TABLE endereco (
    id_endereco INT AUTO_INCREMENT PRIMARY KEY,
    rua VARCHAR(150),
    numero VARCHAR(20),
    bairro VARCHAR(100),
    cep VARCHAR(15),
    id_cidade INT NOT NULL,
    FOREIGN KEY (id_cidade) REFERENCES cidade(id_cidade) ON DELETE CASCADE
);

-- Cliente
CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    telefone VARCHAR(30),
    email VARCHAR(100),
    id_endereco INT,
    FOREIGN KEY (id_endereco) REFERENCES endereco(id_endereco) ON DELETE SET NULL
);

-- Fornecedor
CREATE TABLE fornecedor (
    id_fornecedor INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    telefone VARCHAR(30),
    email VARCHAR(100),
    id_endereco INT,
    FOREIGN KEY (id_endereco) REFERENCES endereco(id_endereco) ON DELETE SET NULL
);

-- Produto
CREATE TABLE produto (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    categoria VARCHAR(100),
    preco DECIMAL(10,2),
    quantidade INT NOT NULL DEFAULT 0,
    estoque_minimo INT DEFAULT 1,
    id_fornecedor INT,
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedor(id_fornecedor) ON DELETE SET NULL
);

-- Venda
CREATE TABLE venda (
    id_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    valor_total DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) ON DELETE SET NULL
);

-- Produto_Venda (itens da venda)
CREATE TABLE produto_venda (
    id_produto_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_venda INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (id_venda) REFERENCES venda(id_venda) ON DELETE CASCADE,
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto) ON DELETE RESTRICT
);

-- Entrada de produtos
CREATE TABLE entrada_produto (
    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL,
    preco_compra DECIMAL(10,2),
    data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_fornecedor INT,
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto) ON DELETE CASCADE,
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedor(id_fornecedor) ON DELETE SET NULL
);
SELECT * FROM produto;
SELECT id_produto, nome, quantidade FROM produto;
UPDATE produto SET quantidade = quantidade + 3 WHERE id_produto = 8;
delete from estado where id_estado >1;
select * from estado;
select * from cidade;
insert into cidade (nome, id_estado) values 
("Ipatinga", 1);

select * from cliente;
select * from endereco;
select * from venda;




