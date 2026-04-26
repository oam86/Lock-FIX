package gaya.pe.kr.core.company.service;

import gaya.pe.kr.core.company.entity.CompanyComputerManagerEntity;
import gaya.pe.kr.core.company.repository.CompanyComputerManagerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class CompanyComputerManagerService {

    @Autowired
    private CompanyComputerManagerRepository repository;

    public List<CompanyComputerManagerEntity> getAllManagers() {
        return repository.findAll();
    }

    public Optional<CompanyComputerManagerEntity> getManagerById(long id) {
        return repository.findById(id);
    }

    public CompanyComputerManagerEntity createManager(CompanyComputerManagerEntity manager) {
        return repository.save(manager);
    }

    public CompanyComputerManagerEntity updateManager(CompanyComputerManagerEntity manager) {
        return repository.save(manager);
    }

    public void deleteManager(long id) {
        repository.deleteById(id);
    }
}