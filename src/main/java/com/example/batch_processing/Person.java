package com.example.batch_processing;

public record Person (String firstName, String lastName) {

    public Person(String firstName, String lastName) {
        this.firstName = firstName;
        this.lastName = lastName;
    }
}
